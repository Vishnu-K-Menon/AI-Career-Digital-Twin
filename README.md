# AI-Career-Digital-Twin
---
title: twin
app_file: app.py
sdk: gradio
sdk_version: 6.14.0
---

# Career Digital Twin

> An AI agent that represents me to recruiters, hiring managers and collaborators. It answers questions about my background, projects and skills in my own voice, records the questions it can't answer, and captures contact details when someone wants to follow up.

**Live demo:** https://huggingface.co/spaces/VKM47/twin

Built as Project 1 (Week 1, Foundations) of Ed Donner's *AI Engineer Agentic Track: The Complete Agent & MCP Course*, then extended with a custom UI, a structured persona document and a tool-calling loop.

---

## What it does

Visitors land on a chat page and talk to "me". Under the hood the agent:

1. **Grounds every answer in two sources** loaded at startup: a long-form professional summary (`summary.txt`) and a text extraction of my LinkedIn profile (`linkedin.pdf`). Both are injected into the system prompt, so the model has my career history, projects, skills and contact details in context rather than guessing.
2. **Stays in character and on topic.** The system prompt scopes the conversation to career, background, skills and experience, steers unrelated questions back, and makes the twin disclose that it is an AI if asked.
3. **Uses tools instead of making things up.** When the model doesn't know an answer, it is instructed to call `record_unknown_question` and then tell the visitor it doesn't know. When a visitor wants to get in touch, it asks for an email and calls `record_user_details`. Both tools send a push notification to my phone via Pushover, so I get a real-time feed of what people ask and who wants to talk.
4. **Runs an agentic loop.** `app.py` keeps calling the model while it returns `tool_calls`, executes each tool, appends the results to the message history, and only returns to the user once the model produces a final text response.

---

## Architecture

```
Visitor (browser)
      │
      ▼
Gradio ChatInterface  ──  styles.py (theme, CSS, JS, header, example prompts)
      │
      ▼
chat(message, history)            app.py
      │
      ├─ system prompt  ◄──────── context.py  ◄── summary.txt + linkedin.pdf (pypdf)
      │
      ▼
OpenAI Chat Completions  ── tools schema ── tools.py
      │
      ├─ finish_reason == "tool_calls" ─► handle_tool_calls()
      │         ├─ record_user_details(email, name, notes)  ─► Pushover
      │         └─ record_unknown_question(question)         ─► Pushover
      │         └─ results appended, loop continues
      │
      ▼
Final assistant message ─► rendered as markdown in the chat
```

---

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Entry point. Builds the Gradio UI, defines `chat()` and the tool-calling loop, launches the app. |
| `context.py` | Reads `summary.txt` and `linkedin.pdf`, assembles `TWIN_SYSTEM_PROMPT` (role, context, rules). |
| `tools.py` | Tool implementations, JSON schemas for function calling, and the `handle_tool_calls` dispatcher. Sends notifications through the Pushover API. |
| `styles.py` | Custom Gradio 6 theme (gold / blue / purple accents), CSS, focus-management JS, branded header, placeholder and example prompts. Dark and light mode supported through theme tokens. |
| `summary.txt` | First-person professional summary used as the twin's primary knowledge source. |
| `linkedin.pdf` | Exported LinkedIn profile, parsed at startup. |
| `requirements.txt` | `gradio`, `openai`, `pypdf`, `python-dotenv`, `requests`. |

---

## Tech stack

- **LLM:** OpenAI Chat Completions API with function calling (model name set by `MODEL_NAME` in `app.py`)
- **Agent pattern:** system-prompt persona + tool-use loop
- **UI:** Gradio 6 (`gr.Blocks` wrapping `gr.ChatInterface`), custom theme via `gr.themes.Base`
- **Document parsing:** `pypdf`
- **Notifications:** Pushover REST API
- **Deployment:** Hugging Face Spaces (Gradio SDK)
- **Config:** `python-dotenv` for local secrets, Space secrets in production

---

## Running locally

**Prerequisites:** Python 3.10+, an OpenAI API key, and a free [Pushover](https://pushover.net/) account (user key + application token) if you want notifications.

```bash
git clone https://github.com/Vishnu-K-Menon/<repo-name>.git
cd <repo-name>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
PUSHOVER_USER=...
PUSHOVER_TOKEN=...
```

Then run:

```bash
python app.py
```

Gradio prints a local URL (default `http://127.0.0.1:7860`). The app will fail at import time if `linkedin.pdf` or `summary.txt` is missing, so make sure both are present.

---

## Deploying to Hugging Face Spaces

The YAML block at the top of this README is the Space configuration (`sdk: gradio`, `app_file: app.py`). To deploy:

1. Create a new Space with the **Gradio** SDK.
2. Push this repository to the Space (or use `gradio deploy` from the project root).
3. In the Space settings, add `OPENAI_API_KEY`, `PUSHOVER_USER` and `PUSHOVER_TOKEN` as **Secrets**. `load_dotenv(override=True)` is a no-op there; the values are read from the environment.
4. The Space builds and serves the app at (https://vkm47-twin.hf.space).

---

## Make it your own

To turn this into *your* twin, you only need to change the content, not the code:

1. Replace `summary.txt` with a first-person description of your background, projects, skills, target roles and how to reach you. The more specific and honest it is, the better the twin answers follow-ups.
2. Export your LinkedIn profile as PDF (Profile → More → Save to PDF) and save it as `linkedin.pdf`.
3. Edit `HEADER_HTML`, `EXAMPLES` and the accent colours in `styles.py` if you want different branding.
4. Optionally set `avatar_images` on the `gr.Chatbot` in `app.py` to show your photo on assistant replies.

---

## Design decisions

- **Two knowledge sources, not one.** The LinkedIn PDF gives structured facts (titles, dates, bullet points); the summary gives narrative, nuance and things LinkedIn doesn't capture (target roles, work authorization, how I think about my work). Together they cover most of what a recruiter asks.
- **"I don't know" is a feature.** Rather than letting the model improvise, unknown questions are logged. That list is the backlog for the next revision of `summary.txt`.
- **Notifications over a database.** For a personal site, a push to my phone is more useful than a table nobody checks. Swapping Pushover for email, Slack or a CRM is a one-function change in `tools.py`.
- **Styling kept out of the logic.** All UI concerns live in `styles.py`, so the agent code stays readable and the look can change without touching the loop.

---



---

## Contact

- Email: vishnumenon@myworkgmail.com
- LinkedIn: https://www.linkedin.com/in/vkm47/
- GitHub: https://github.com/Vishnu-K-Menon
- Or just ask the twin: https://huggingface.co/spaces/VKM47/twin
