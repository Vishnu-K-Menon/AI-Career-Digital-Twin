import json
import os
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import requests
from dotenv import load_dotenv
from huggingface_hub import CommitScheduler

load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


def push(text):
    print(f"Push: {text}", flush=True)
    requests.post(
        pushover_url,
        data={"token": pushover_token, "user": pushover_user, "message": text},
        timeout=10,
    )


# --------------------------------------------------------------------------- GitHub
GITHUB_USER = "Vishnu-K-Menon"
GITHUB_CACHE_SECONDS = 60 * 60   # everyone on the Space shares one IP's rate limit (60 requests/hour without a token)
github_cache = {"fetched_at": 0.0, "repos": None}


def fetch_github_repos():
    if github_cache["repos"] is not None and time.time() - github_cache["fetched_at"] < GITHUB_CACHE_SECONDS:
        return github_cache["repos"]
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"
    response = requests.get(
        f"https://api.github.com/users/{GITHUB_USER}/repos",
        params={"sort": "pushed", "per_page": 30},
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    repos = [
        {
            "name": repo["name"],
            "description": repo["description"] or "",
            "language": repo["language"],
            "stars": repo["stargazers_count"],
            "last_pushed": repo["pushed_at"][:10],
            "url": repo["html_url"],
        }
        for repo in response.json()
        # skip forks, and the profile repos that aren't projects (profile README and the github.io site)
        if not repo["fork"] and repo["name"] != GITHUB_USER and not repo["name"].endswith(".github.io")
    ]
    github_cache.update(repos=repos, fetched_at=time.time())
    return repos


def get_github_projects(limit=6):
    return fetch_github_repos()[:limit]


# --------------------------------------------------------------------------- Permanent log (private HF dataset)
# Lines are written to a temp folder (so local runs never leave files in twin/, which `gradio deploy` uploads)
# and CommitScheduler pushes that folder to the dataset every 5 minutes. Without HF_TOKEN the log stays local.
LOG_REPO = os.getenv("TWIN_LOG_REPO", "VKM47/twin-logs")
LOG_DIR = Path(tempfile.gettempdir()) / "twin_logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"events-{uuid4()}.jsonl"   # a new file per run, so two runs never overwrite each other

scheduler = None
log_lock = threading.Lock()
if os.getenv("HF_TOKEN"):
    try:
        scheduler = CommitScheduler(
            repo_id=LOG_REPO,
            repo_type="dataset",
            folder_path=LOG_DIR,
            path_in_repo="logs",
            every=5,
            private=True,
            token=os.getenv("HF_TOKEN"),
        )
        log_lock = scheduler.lock
    except Exception as e:
        print(f"Log upload disabled, logging locally only: {e}", flush=True)
else:
    print("HF_TOKEN not set: logging locally only", flush=True)


def log_event(kind, payload):
    record = {"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **payload}
    with log_lock:   # the uploader runs in the background; the lock stops it uploading half a line
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


# --------------------------------------------------------------------------- Lead email (Resend)
RESEND_URL = "https://api.resend.com/emails"


def field(message, key):
    # Messages are dicts (ours, Gradio's) or SDK objects; read either
    return message.get(key) if isinstance(message, dict) else getattr(message, key, None)


def as_text(content):
    # Plain strings, Gradio 6's {"type": "text", "text": ...} blocks, or Claude's content blocks
    # (text, thinking, tool_use, tool_result): only the text blocks are conversation
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(field(block, "text") or "" for block in content if field(block, "type") == "text")
    return ""


def format_transcript(messages):
    lines = []
    for message in messages:
        role = field(message, "role")
        text = as_text(field(message, "content")).strip()
        if role in ("user", "assistant") and text:
            lines.append(f"{'Visitor' if role == 'user' else 'Twin'}: {text}")
    return "\n\n".join(lines)


def send_lead_email(name, email, phone, notes, transcript):
    if not (os.getenv("RESEND_API_KEY") and os.getenv("LEAD_EMAIL_TO")):
        print("Lead email skipped: RESEND_API_KEY or LEAD_EMAIL_TO not set", flush=True)
        return None
    body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nNotes: {notes}\n\nConversation:\n\n{transcript}"
    response = requests.post(
        RESEND_URL,
        headers={"Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}"},
        json={
            "from": "Digital Twin <onboarding@resend.dev>",
            "to": [os.getenv("LEAD_EMAIL_TO")],
            "reply_to": email,          # so Reply in the inbox goes straight to the visitor
            "subject": f"New lead from your twin: {name} <{email}>",
            "text": body,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["id"]


# --------------------------------------------------------------------------- Tools
def record_user_details(email, name="Name not provided", phone="not provided", notes="not provided", transcript=""):
    if "@" not in email:   # no real email yet: tell the model to ask for it instead of recording a lead
        return "No email yet. Ask the visitor for their email address, then call this tool again."
    push(f"Recording interest from {name} with email {email}, phone {phone} and notes {notes}")
    log_event("lead", {"email": email, "name": name, "phone": phone, "notes": notes})
    try:
        send_lead_email(name, email, phone, notes, transcript or "(no conversation captured)")
    except Exception as e:
        # The push and the log already have the lead, so the visitor still gets an OK
        print(f"Lead email failed: {e}", flush=True)
    return "OK"


def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    log_event("unknown_question", {"question": question})
    return "OK"


# Claude tool definitions. eager_input_streaming streams tool inputs as they are generated; the server then
# no longer validates them, so handle_tool_calls checks each input before running the tool.
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address. Only use this after the user has given you their own email address.",
    "eager_input_streaming": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "phone": {"type": "string", "description": "The user's phone number, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "eager_input_streaming": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

get_github_projects_json = {
    "name": "get_github_projects",
    "description": "Get Vishnu's public GitHub repositories, most recently updated first. Use this when someone asks what he is working on now, about his projects, or about his code.",
    "eager_input_streaming": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "How many repositories to return (default 6)"},
        },
        "required": [],
        "additionalProperties": False,
    },
}

tools = [record_user_details_json, record_unknown_question_json, get_github_projects_json]
schemas = {tool["name"]: tool["input_schema"] for tool in tools}

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
    "get_github_projects": get_github_projects,
}


TYPES = {"string": str, "integer": int}


def input_problem(tool_name, arguments):
    # With eager input streaming the server doesn't validate tool inputs, so check them against the schema
    if not isinstance(arguments, dict):
        return "input is not an object"
    properties = schemas[tool_name]["properties"]
    for key in schemas[tool_name]["required"]:
        if key not in arguments:
            return f"missing required field '{key}'"
    for key, value in arguments.items():
        if key not in properties:
            return f"unexpected field '{key}'"
        expected = TYPES.get(properties[key]["type"])
        if expected and (not isinstance(value, expected) or isinstance(value, bool)):
            return f"field '{key}' should be a {properties[key]['type']}"
    return None


def handle_tool_calls(tool_uses, messages):
    # tool_uses: the response's tool_use blocks. Returns one tool_result per block, to send back in a single user turn.
    results = []
    for block in tool_uses:
        print(f"Tool called: {block.name}", flush=True)
        tool = tool_map.get(block.name)
        problem = f"Unknown tool: {block.name}" if tool is None else input_problem(block.name, block.input)
        if problem:
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": problem, "is_error": True})
            continue
        arguments = dict(block.input)
        if block.name == "record_user_details":
            arguments["transcript"] = format_transcript(messages)   # our code adds the conversation, not the model
        try:
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(tool(**arguments))})
        except Exception as e:
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": f"Tool error: {e}", "is_error": True})
    return results
