---
title: twin
app_file: app.py
sdk: gradio
sdk_version: 6.14.0
---

# Career Digital Twin

> An AI agent that represents me to recruiters, hiring managers and collaborators. It answers questions about my background, projects and skills in my own voice, checks my GitHub live for what I'm building now, records the questions it can't answer, and passes contact details to me by push and email when someone wants to follow up.

**Live demo:** https://huggingface.co/spaces/VKM47/twin (direct: https://vkm47-twin.hf.space)

Built as Project 1 (Week 1, Foundations) of Ed Donner's *AI Engineer Agentic Track: The Complete Agent & MCP Course*, then extended with Claude, streaming with visible tool steps, three tools, lead emails with the conversation transcript, a permanent log and a recruiter-first UI.

---

## What it does

Visitors land on a page with my photo, role, résumé download and selected work on one side, and a chat with "me" on the other. Under the hood the agent:

1. **Grounds every answer in two sources** loaded at startup: a long-form professional summary (`summary.txt`) and a text extraction of my LinkedIn profile (`linkedin.pdf`). Both go into the system prompt, so the model has my career history, projects, skills and contact details in context rather than guessing.
2. **Checks GitHub live.** When someone asks what I'm working on now, or about a project or technology, it calls `get_github_projects`, which reads my public repositories from the GitHub API (most recently pushed first, forks and profile repos skipped). Results are cached for an hour so every visitor shares one request.
3. **Captures leads.** When a visitor wants to get in touch, it asks for their email (required), plus a phone number and a short note (both optional), and calls `record_user_details`. I get a Pushover notification on my phone and an email through Resend with their details **and the whole conversation**, with reply-to set to the visitor so I can answer straight from my inbox. The tool refuses anything without an `@`, so the model can't record a lead before the visitor has actually given an email.
4. **Says "I don't know" instead of improvising.** Questions it can't answer from the sources go to `record_unknown_question`, which pushes them to my phone. That list is the backlog for the next revision of `summary.txt`.
5. **Keeps a permanent log.** Every lead and unknown question is also written as a JSON line and uploaded every five minutes to a private Hugging Face dataset, so nothing is lost when the Space restarts.
6. **Streams, and shows its work.** Replies stream token by token. When it uses a tool, the chat shows a step such as "Checking my GitHub" that turns from pending to done with its duration.
7. **Stays in character and on topic.** The system prompt scopes the conversation to career, background, skills and experience, steers unrelated questions back, and makes the twin say it is an AI if asked.

---

## Architecture

```
Visitor (browser)
      │
      ▼
Gradio 6 Blocks  ──  styles.py (theme tokens, CSS, hero, work card, chips, light + dark)
      │
      ▼
chat_stream(message, history)                                  app.py
      │
      ├─ system prompt (cached) ◄── context.py ◄── summary.txt + linkedin.pdf (pypdf)
      │
      ▼
Claude Messages API, streaming  (claude-haiku-5-5, effort "medium")
      │
      ├─ text deltas ─────────────────────────────► streamed into the chat bubble
      │
      ├─ stop_reason "tool_use" ─► tool step shown (pending)
      │        │
      │        ▼
      │   handle_tool_calls()  (validates each input against its schema)   tools.py
      │        ├─ get_github_projects(limit)                ─► GitHub REST API (1 h cache)
      │        ├─ record_user_details(email, name, phone, notes)
      │        │        ─► Pushover + Resend email (with transcript) + HF dataset log
      │        └─ record_unknown_question(question)         ─► Pushover + HF dataset log
      │        │
      │        ▼
      │   all tool_result blocks sent back in one user turn, step marked done
      │   loop continues (up to 5 tool rounds)
      │
      ▼
Final answer, rendered as markdown
```

---

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Entry point. Builds the page (hero, work card, chat), defines `chat_stream()`: the streaming Claude call, the tool loop, tool steps in the chat, friendly errors. Launches the app. |
| `context.py` | Reads `summary.txt` and `linkedin.pdf` and assembles `TWIN_SYSTEM_PROMPT` (role, context, rules for leads, GitHub and unknown questions). |
| `tools.py` | The three tools and their Claude tool definitions, input validation, `handle_tool_calls`, the Pushover push, the Resend lead email with transcript, the GitHub fetch and cache, and the HF dataset log (`CommitScheduler`). |
| `styles.py` | Gradio 6 theme and CSS: green wall with brass accent, light and dark palettes as tokens, hero with photo and résumé download, the selected-work and "Get in touch" card, chip icons, example prompts. |
| `assets/` | `vishnu-512.jpg` (portrait and chat avatar) and the résumé PDF behind the download button. |
| `summary.txt` | First-person professional summary, the twin's primary knowledge source. |
| `linkedin.pdf` | Exported LinkedIn profile, parsed at startup. |
| `requirements.txt` | `anthropic`, `gradio`, `huggingface_hub`, `pypdf`, `python-dotenv`, `requests`. |

---

## Tech stack

- **LLM:** Claude Haiku 5.5 (`claude-haiku-5-5`) through the Anthropic Python SDK: Messages API streaming, tool use, prompt caching on the system prompt
- **Agent pattern:** system-prompt persona + manual streaming tool-use loop
- **UI:** Gradio 6.14 (`gr.Blocks` around `gr.ChatInterface`), custom theme via `gr.themes.Base`, `gr.ChatMessage` metadata for tool steps
- **Tools / integrations:** GitHub REST API, Pushover, Resend (HTTP email API), Hugging Face Hub `CommitScheduler`
- **Document parsing:** `pypdf`
- **Deployment:** Hugging Face Spaces (Gradio SDK)
- **Config:** `python-dotenv` locally, Space secrets in production

---

## Running locally

**Prerequisites:** Python 3.10+ and an [Anthropic API key](https://console.anthropic.com/). Everything else is optional.

```bash
git clone https://github.com/Vishnu-K-Menon/AI-Career-Digital-Twin.git
cd AI-Career-Digital-Twin

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-...

# Optional
PUSHOVER_USER=...
PUSHOVER_TOKEN=...
RESEND_API_KEY=re_...
LEAD_EMAIL_TO=you@example.com
GITHUB_TOKEN=...
HF_TOKEN=hf_...
TWIN_LOG_REPO=your-username/twin-logs
```

| Variable | Needed for | If it's missing |
|---|---|---|
| `ANTHROPIC_API_KEY` | The model | The app can't answer. **Required.** |
| `PUSHOVER_USER`, `PUSHOVER_TOKEN` | Push notifications for leads and unknown questions | The push request fails quietly; everything else still works. |
| `RESEND_API_KEY`, `LEAD_EMAIL_TO` | The lead email with the transcript | The email is skipped (logged as "Lead email skipped"). |
| `GITHUB_TOKEN` | A higher GitHub rate limit | Unauthenticated requests (60 an hour), which the one-hour cache keeps well within. |
| `HF_TOKEN` | Uploading the log to a private HF dataset (write access) | The log stays in a local temp folder ("HF_TOKEN not set: logging locally only"). |
| `TWIN_LOG_REPO` | Which dataset the log goes to | Defaults to `VKM47/twin-logs`; set your own. |

Then run:

```bash
python app.py
```

Gradio prints a local URL (default `http://127.0.0.1:7860`). The app fails at import time if `linkedin.pdf` or `summary.txt` is missing, so make sure both are present.

---

## Deploying to Hugging Face Spaces

The YAML block at the top of this README is the Space configuration (`sdk: gradio`, `sdk_version: 6.14.0`, `app_file: app.py`). To deploy:

1. Create a new Space with the **Gradio** SDK.
2. Upload this repository to the Space (`gradio deploy` from the project root, or `HfApi().upload_folder`).
3. In the Space settings, add the variables above as **Secrets** (at least `ANTHROPIC_API_KEY`). `load_dotenv(override=True)` is a no-op there; the values come from the environment. Restart the Space after adding secrets.
4. The Space builds and serves the app (mine is at https://vkm47-twin.hf.space).

Two things that only show up on Spaces, both already handled in `app.py`:

- **`cache_examples=False`** on the `ChatInterface`. Spaces caches example prompts at startup by running them, and that crashes on replies that contain tool steps.
- **`ssr_mode=False`** in `launch()`. With server-side rendering on, Gradio's default prose styles override the custom CSS.

**Resend note:** emails are sent from Resend's shared sender `onboarding@resend.dev`, which only delivers to the address your Resend account was created with. Set `LEAD_EMAIL_TO` to that address, or verify your own domain in Resend and change the `from` in `tools.py`.

---

## Make it your own

To turn this into *your* twin, you mostly change content, not code:

1. Replace `summary.txt` with a first-person description of your background, projects, skills, target roles and how to reach you. The more specific and honest it is, the better the twin answers follow-ups.
2. Export your LinkedIn profile as PDF (Profile → More → Save to PDF) and save it as `linkedin.pdf`.
3. Put your photo at `assets/vishnu-512.jpg` (a square crop around 512 px) and your résumé at `assets/Vishnu-K-Menon-Resume.pdf`, or change `PHOTO_PATH` and `RESUME_PATH` in `styles.py`.
4. Edit `HERO_HTML`, `LABEL_HTML`, `PLACEHOLDER_HTML`, `EXAMPLES` and the `LIGHT` / `DARK` palettes in `styles.py` for your own name, links, work and colours.
5. Set `GITHUB_USER` in `tools.py` to your GitHub username.

---

## Design decisions

- **Two knowledge sources, not one.** The LinkedIn PDF gives structured facts (titles, dates, bullet points); the summary gives narrative, nuance and things LinkedIn doesn't capture (target roles, work authorization, how I think about my work). Together they cover most of what a recruiter asks.
- **GitHub for anything current.** A summary goes stale; the GitHub tool means "what are you building now?" gets today's answer.
- **"I don't know" is a feature.** Rather than letting the model improvise, unknown questions are logged. That list is the backlog for the next revision of `summary.txt`.
- **Push for speed, email for context, a dataset for the record.** The push tells me someone wants to talk; the email gives me the whole conversation and a reply button; the HF dataset keeps everything after the Space restarts. Spaces block outbound SMTP, so the email goes through Resend's HTTP API.
- **Email required, phone optional.** The email is how I reply, so the tool won't record a lead without one; a phone number and note are welcome but never forced.
- **Show the tool steps.** Seeing "Checking my GitHub" makes the pause before a tool-based answer read as work, not lag.
- **Claude Haiku 5.5.** Fast and cheap enough for a public page ($0.10 / $0.50 per million input / output tokens), and the system prompt (about 7K tokens with the tool definitions) is cached, so repeat turns read it at a tenth of the price.
- **Styling kept out of the logic.** All UI concerns live in `styles.py`, built on theme tokens first and CSS second, so the agent code stays readable and the look can change without touching the loop.

---

## Contact

- Email: vishnumenon@myworkgmail.com
- LinkedIn: https://www.linkedin.com/in/vkm47/
- GitHub: https://github.com/Vishnu-K-Menon
- Or just ask the twin: https://huggingface.co/spaces/VKM47/twin
