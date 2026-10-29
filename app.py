import time

import anthropic
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls, field, as_text
from styles import (THEME, CSS, HEAD, HERO_HTML, LABEL_HTML, PLACEHOLDER_HTML,
                    EXAMPLES, EXAMPLE_LABELS, PHOTO_PATH, photo_uri)
from dotenv import load_dotenv
import gradio as gr

load_dotenv(override=True)

MODEL_NAME = "claude-haiku-5-5"
EFFORT = "medium"     # Haiku 5.5's default; "low" is cheaper but more likely to skip the GitHub check
MAX_TOKENS = 64000    # a ceiling, not a target: streaming keeps long answers within HTTP timeouts
MAX_TOOL_ROUNDS = 5
FRIENDLY_ERROR = "Sorry, I couldn't reach my model just now. Please try again in a moment."
DECLINED = "I can't help with that one. Ask me anything about Vishnu's work, projects or experience."

TOOL_STEPS = {
    # tool name: (title while it runs, text once it's done)
    "get_github_projects": ("Checking my GitHub", "Pulled the live list of repositories."),
    "record_user_details": ("Passing your details to Vishnu", "Sent. Vishnu will get back to you."),
    "record_unknown_question": ("Noting this question for Vishnu", "Logged for Vishnu to answer."),
}

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY


def clean_history(history):
    # Gradio 6 history has extra keys and text stored as blocks; tool-step bubbles (metadata title) are UI only
    cleaned = []
    for message in history:
        if (field(message, "metadata") or {}).get("title"):
            continue
        text = as_text(field(message, "content")).strip()
        if text:
            cleaned.append({"role": field(message, "role"), "content": text})
    return cleaned


def chat_stream(message, history):
    messages = clean_history(history) + [{"role": "user", "content": message}]
    shown = []   # bubbles already finished this turn: tool steps, plus any text written before a tool call
    json_retries = 0

    for _ in range(MAX_TOOL_ROUNDS + 1):
        text = ""
        try:
            with client.messages.stream(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                system=TWIN_SYSTEM_PROMPT,
                cache_control={"type": "ephemeral"},   # the long system prompt is the same on every turn
                tools=tools,
                output_config={"effort": EFFORT},
                messages=messages,
            ) as stream:
                for event in stream:
                    if event.type == "text":
                        text += event.text
                        yield shown + [gr.ChatMessage(role="assistant", content=text)]
                response = stream.get_final_message()
            json_retries = 0
        except ValueError as e:
            # A streamed tool input the SDK couldn't parse at all: re-ask the same turn once
            print(f"Unparseable tool input: {e}", flush=True)
            json_retries += 1
            if json_retries > 1:
                yield shown + [gr.ChatMessage(role="assistant", content=FRIENDLY_ERROR)]
                return
            continue
        except anthropic.APIError as e:
            print(f"Model error: {e}", flush=True)
            yield shown + [gr.ChatMessage(role="assistant", content=FRIENDLY_ERROR)]
            return

        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if response.stop_reason == "refusal":
            yield shown + [gr.ChatMessage(role="assistant", content=DECLINED)]
            return
        if not tool_uses:   # a normal answer, so we're done
            if not text:
                yield shown + [gr.ChatMessage(role="assistant", content=FRIENDLY_ERROR)]
            return
        if response.stop_reason == "max_tokens":   # a cut-off tool input: don't run it
            yield shown + [gr.ChatMessage(role="assistant", content=FRIENDLY_ERROR)]
            return

        if text:
            shown.append(gr.ChatMessage(role="assistant", content=text))
        # The whole assistant turn goes back unchanged, thinking blocks included
        messages.append({"role": "assistant", "content": response.content})

        steps = []
        for block in tool_uses:
            title, _ = TOOL_STEPS.get(block.name, (f"Using {block.name}", "Done."))
            step = gr.ChatMessage(role="assistant", content="", metadata={"title": title, "status": "pending"})
            shown.append(step)
            steps.append((block, step))
        yield list(shown)

        started = time.time()
        results = handle_tool_calls(tool_uses, messages)
        for block, step in steps:
            step.content = TOOL_STEPS.get(block.name, ("", "Done."))[1]
            step.metadata.update(status="done", duration=round(time.time() - started, 1))
        yield list(shown)
        # Every tool result goes back in one user turn
        messages.append({"role": "user", "content": results})

    yield shown + [gr.ChatMessage(role="assistant", content="That took more steps than I'm allowed. Could you ask it a different way?")]


if __name__ == "__main__":
    # The hero on top, then the profile card and the chat side by side (they stack on a phone, chat first).
    # (Gradio 6: theme/css/head go on launch(); the script ships in HEAD because launch(js=...) doesn't run.)
    with gr.Blocks(title="Vishnu K Menon · Digital Twin") as demo:
        gr.HTML(HERO_HTML, elem_id="twin-hero")
        with gr.Row(elem_id="twin-row", equal_height=False):
            with gr.Column(scale=4, min_width=300, elem_id="twin-label"):
                gr.HTML(LABEL_HTML)
            with gr.Column(scale=7, min_width=340, elem_id="twin-chat-col"):
                gr.ChatInterface(
                    chat_stream,
                    examples=EXAMPLES,
                    example_labels=EXAMPLE_LABELS,
                    cache_examples=False,   # Spaces caches examples at startup by default: costly, and it rejects tool-step messages
                    chatbot=gr.Chatbot(
                        elem_id="twin-chat",
                        show_label=False,
                        layout="bubble",
                        placeholder=PLACEHOLDER_HTML,
                        buttons=["copy"],     # copy on each reply; no share button or toolbar
                        avatar_images=(None, PHOTO_PATH) if photo_uri else None,
                    ),
                    textbox=gr.Textbox(
                        elem_id="twin-input",
                        placeholder="Ask about my work…",
                        show_label=False,
                        submit_btn=True,
                        stop_btn=True,          # lets the visitor stop a long answer while it streams
                    ),
                )

    # ssr_mode=False: Spaces turns on Gradio's experimental server-side rendering, which renders the HTML blocks
    # differently from a normal run and lets Gradio's default prose styles win over ours.
    demo.launch(theme=THEME, css=CSS, head=HEAD, show_error=True, ssr_mode=False)
