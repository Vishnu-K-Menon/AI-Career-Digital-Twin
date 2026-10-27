from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls
from styles import THEME, CSS, JS, EXAMPLES, HEADER_HTML, PLACEHOLDER_HTML
from dotenv import load_dotenv
import gradio as gr

load_dotenv(override=True)

MODEL_NAME = "gpt-6-luna"

openai = OpenAI()

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def chat(message, history):
    messages = system + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools, reasoning_effort="none")
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools, reasoning_effort="none")
    return response.choices[0].message.content


if __name__ == "__main__":
    # Blocks wrapper lets us put a branded header above the chat.
    # ChatInterface's own title/description are left unset so they don't
    # render a second heading. (Gradio 6: theme/css/js go on launch().)
    with gr.Blocks(title="Digital Twin") as demo:
        gr.HTML(HEADER_HTML)
        gr.ChatInterface(
            chat,
            examples=EXAMPLES,
            chatbot=gr.Chatbot(
                elem_id="twin-chat",
                show_label=False,
                layout="bubble",
                height=520,
                placeholder=PLACEHOLDER_HTML,
                # avatar_images=(None, "assets/avatar.png"),  # optional: your photo on bot replies
            ),
            textbox=gr.Textbox(
                elem_id="twin-input",
                placeholder="Ask me anything about my work…",
                show_label=False,
                submit_btn=True,
            ),
        )

    demo.launch(theme=THEME, css=CSS, js=JS)