"""Styling for the digital-twin Gradio app.

Usage
-----
    from styles import THEME, CSS, HEAD, HERO_HTML, LABEL_HTML, PLACEHOLDER_HTML, EXAMPLES, EXAMPLE_LABELS, PHOTO_PATH

app.py builds the page (hero, then the profile card beside the chat) and passes THEME / CSS / HEAD to demo.launch().

Design notes (the full record is 1_foundations/DESIGN.md)
------------
* A deep green wall painted edge to edge, content centred at 1240px; two surface steps (cards, then the
  raised chips / composer / your messages).
* One accent, brass amber, in three tones (fill, text, edge) on everything you can act on or that is
  happening now: send/stop, links, chip hover, the stripe on the twin's replies, the live-step dot, focus.
* Archivo in one family; cards 16px, controls 12px; no shadows except the composer's focus halo.
* Gradio 6 quirks handled here: custom CSS inside @media is re-scoped under .contain (so the container padding
  uses clamp()), launch(js=...) doesn't run (so the script ships in HEAD), and the example prompts are
  button[aria-label] (so the toolbar rules exclude .example).
"""

import base64
import mimetypes
from pathlib import Path
from urllib.parse import quote

import gradio as gr

# The photo appears in the hero and as the twin's avatar; the résumé becomes a download button.
# Paths are relative to twin/, where the app runs. Set either to None to hide it.

PHOTO_PATH = "assets/vishnu-512.jpg"     # square 512px copy of assets/vishnu.png, so the page stays light
RESUME_PATH = "assets/Vishnu-K-Menon-Resume.pdf"


def data_uri(path):
    # Embed a small file straight into the page, so no static-file setup is needed (locally or on the Space)
    if not path or not Path(path).exists():
        return None
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(Path(path).read_bytes()).decode()


def svg_icon(paths):
    # A 24x24 outline icon (Lucide style) as a CSS mask, so CSS can colour it for each theme and on hover
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
           f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>')
    return 'url("data:image/svg+xml,' + quote(svg) + '")'


photo_uri = data_uri(PHOTO_PATH)
resume_uri = data_uri(RESUME_PATH)

# One icon per starter chip, in the same order as EXAMPLES below
CHIP_ICONS = [
    svg_icon('<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/>'
             '<path d="M18 9a9 9 0 0 1-9 9"/>'),                                             # git branch: what are you building
    svg_icon('<path d="M10 2v7.5a2 2 0 0 1-.2.9L4.7 20.6a1 1 0 0 0 .9 1.4h12.8a1 1 0 0 0 .9-1.4l-5.1-10.2a2 2 0 0 1-.2-.9V2"/>'
             '<path d="M8.5 2h7"/><path d="M7 16h10"/>'),                                     # flask: TheraMind
    svg_icon('<path d="M20 10c0 5-5.5 10.2-7.4 11.8a1 1 0 0 1-1.2 0C9.5 20.2 4 15 4 10a8 8 0 0 1 16 0"/>'
             '<circle cx="12" cy="10" r="3"/>'),                                              # map pin: relocation
    svg_icon('<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-9 5.7a2 2 0 0 1-2 0L2 7"/>'),  # mail: talk about a role
]

# The palette: one wall, two surface steps, ink, muted, and one accent (brass amber) with three tones.
# Every text pair is at least 4.5:1; every control edge at least 3:1.

LIGHT = dict(
    wall="#13342f",          # the deep green page ground
    wall_text="#eef1ec",     # hero text on the wall (11.8:1)
    wall_muted="#b8c6c0",    # hero pitch on the wall (7.6:1)
    surface="#f3f4f2",       # the two cards
    raised="#ffffff",        # chips, composer, your own messages
    line="#d6dad5",          # hairlines inside the cards
    card_edge="transparent", # light cards already stand clear of the wall
    ink="#151917",           # body text (16:1)
    muted="#4e5753",         # secondary text (6.8:1)
    accent="#e3a72f",        # brass amber: buttons and fills
    accent_hover="#c98e14",
    on_accent="#1a1206",     # text and icons on amber (8.7:1)
    accent_text="#8a5b00",   # amber for links on light surfaces (5.3:1)
    accent_edge="#9a6a0c",   # amber borders, the reply stripe, focus (4.3:1)
    control_edge="#858f8a",  # resting edge of the composer (3:1); chips rest on the quieter line
)
DARK = dict(
    wall="#0b1f1b",
    wall_text="#eef1ec",
    wall_muted="#b8c6c0",
    surface="#24322e",       # 1.28:1 against the wall
    raised="#2e3d39",
    line="#3b4a46",
    card_edge="rgba(255, 255, 255, 0.07)",   # dark on dark needs an edge to read as a card
    ink="#eef1ec",
    muted="#a3b2ad",
    accent="#e3a72f",
    accent_hover="#f0bb4f",
    on_accent="#1a1206",
    accent_text="#f2c063",
    accent_edge="#e3a72f",
    control_edge="#7e8a85",   # 3.2:1 on the raised surface
)

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.amber,
    neutral_hue=gr.themes.colors.stone,
    radius_size=gr.themes.sizes.radius_lg,
    spacing_size=gr.themes.sizes.spacing_md,
    text_size=gr.themes.sizes.text_md,
    font=(gr.themes.GoogleFont("Archivo"), "ui-sans-serif", "system-ui", "sans-serif"),
    font_mono=(gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"),
).set(
    body_background_fill=LIGHT["wall"],
    body_background_fill_dark=DARK["wall"],
    body_text_color=LIGHT["ink"],
    body_text_color_dark=DARK["ink"],
    body_text_color_subdued=LIGHT["muted"],
    body_text_color_subdued_dark=DARK["muted"],
    background_fill_primary=LIGHT["surface"],
    background_fill_primary_dark=DARK["surface"],
    background_fill_secondary=LIGHT["surface"],
    background_fill_secondary_dark=DARK["surface"],
    block_background_fill=LIGHT["surface"],
    block_background_fill_dark=DARK["surface"],
    block_border_width="0px",
    block_shadow="none",
    block_shadow_dark="none",
    border_color_primary=LIGHT["line"],
    border_color_primary_dark=DARK["line"],
    color_accent=LIGHT["accent"],
    color_accent_soft="#fbf0d6",
    color_accent_soft_dark="#3a2e12",
    link_text_color=LIGHT["accent_text"],
    link_text_color_dark=DARK["accent_text"],
    input_background_fill=LIGHT["raised"],
    input_background_fill_dark=DARK["raised"],
    input_border_color=LIGHT["control_edge"],
    input_border_color_dark=DARK["control_edge"],
    input_border_color_focus=LIGHT["accent_edge"],
    input_border_color_focus_dark=DARK["accent_edge"],
    input_shadow_focus="none",
    input_placeholder_color="#5f6763",
    input_placeholder_color_dark="#9ca8a3",
    button_primary_background_fill=LIGHT["accent"],
    button_primary_background_fill_hover=LIGHT["accent_hover"],
    button_primary_background_fill_dark=DARK["accent"],
    button_primary_background_fill_hover_dark=DARK["accent_hover"],
    button_primary_text_color=LIGHT["on_accent"],
    button_primary_text_color_dark=DARK["on_accent"],
    button_secondary_background_fill="transparent",
    button_secondary_text_color=LIGHT["ink"],
    button_secondary_text_color_dark=DARK["ink"],
    chatbot_text_size="*text_md",
)

# The words on the page. Every fact comes from summary.txt; links are the real ones.

portrait = (
    f'<img class="hero-photo" src="{photo_uri}" alt="Vishnu K Menon">'
    if photo_uri else '<div class="hero-photo hero-monogram" aria-hidden="true">VM</div>'
)
resume_button = (
    f'<a class="hero-cta" href="{resume_uri}" download="Vishnu-K-Menon-Resume.pdf">Download résumé</a>'
    if resume_uri else ""
)

HERO_HTML = f"""
<header class="hero">
  {portrait}
  <div class="hero-text">
    <h1 class="hero-name">Vishnu K Menon</h1>
    <p class="hero-role">AI/ML Engineer at C3 AI · LLM and RAG systems</p>
    <p class="hero-pitch">I turn LLM prototypes into production systems: retrieval, orchestration, evaluation, deployment and monitoring.</p>
  </div>
  <nav class="hero-links" aria-label="Résumé and profiles">
    {resume_button}
    <a href="https://www.linkedin.com/in/vkm47/" target="_blank" rel="noopener">LinkedIn</a>
    <a href="https://github.com/Vishnu-K-Menon" target="_blank" rel="noopener">GitHub</a>
    <a href="mailto:vishnumenon@myworkgmail.com">Email</a>
  </nav>
</header>
"""

LABEL_HTML = """
<aside class="wall-label" aria-label="About Vishnu">
  <p class="wl-medium">LLM and RAG systems · LangGraph · fine-tuning with QLoRA and DPO · Python on AWS</p>
  <p class="wl-meta">Buffalo, New York. Open to remote, hybrid or relocating anywhere in the US.</p>

  <h2 class="wl-heading">Selected work</h2>
  <ul class="wl-work">
    <li><strong>C3 AI document intelligence</strong>
        <span class="wl-desc">Multi-tenant LLM and RAG platform, 1M+ requests a day across 20+ enterprise deployments.</span></li>
    <li><strong>TheraMind</strong>
        <span class="wl-desc">Dual-mode clinical LLM agent, fine-tuned Llama 3.2 with QLoRA and DPO.</span>
        <a href="https://vkm47-theramind-ai.hf.space" target="_blank" rel="noopener">Live demo</a></li>
    <li><strong>LEDGER</strong>
        <span class="wl-desc">Self-verifying RAG that checks every claim against its source; 223 tests in CI.</span>
        <a href="https://github.com/Vishnu-K-Menon/LEDGER" target="_blank" rel="noopener">Code</a></li>
  </ul>

  <h2 class="wl-heading wl-contact-heading">Get in touch</h2>
  <p class="wl-contact">Leave your email, phone and a short note in the chat. I'll pass them to Vishnu.</p>
</aside>
"""

PLACEHOLDER_HTML = """
<div class="chat-start">
  <p class="chat-greeting">Hi, I'm Vishnu's AI twin. Ask me what you'd ask in a first call.</p>
  <ul class="chat-how" aria-label="What this twin can do">
    <li><strong>Answers from his résumé and LinkedIn,</strong> and says so when something isn't there.</li>
    <li><strong>Checks his GitHub live</strong> when you ask what he's building now.</li>
    <li><strong>Passes your message to Vishnu</strong> by email when you leave your email, phone and a note.</li>
  </ul>
</div>
"""

EXAMPLES = [   # what gets sent when a chip is clicked
    "What are you working on right now?",
    "Walk me through TheraMind.",
    "Are you open to relocating, and what's your work authorization?",
    "I'd like to talk to you about a role.",
]
EXAMPLE_LABELS = [   # what the chip shows
    "What are you building now?",
    "Walk me through TheraMind",
    "Relocation and work authorization",
    "Talk to me about a role",
]

def tokens(p):
    return "\n".join(f"  --{k.replace('_', '-')}: {v};" for k, v in p.items())


chip_icon_rules = "\n".join(
    f"#twin-chat .examples .example:nth-child({i}) .example-content::before {{ -webkit-mask-image: {icon}; mask-image: {icon}; }}"
    for i, icon in enumerate(CHIP_ICONS, start=1)
)

CSS = f"""
:root {{
{tokens(LIGHT)}
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
}}
.dark {{
{tokens(DARK)}
}}

/* Gradio chrome we don't need */
footer, .built-with, .show-api, .api-docs {{ display: none !important; }}

/* ---------- The wall: painted edge to edge, content centred at 1240px ---------- */
html, body, gradio-app {{ background: var(--wall) !important; }}
body .gradio-container {{
  width: 100% !important; max-width: 1240px !important;   /* fixed width, so nothing shifts while a reply streams */
  margin: 0 auto !important;
  padding: clamp(16px, 3vw, 40px) clamp(16px, 2.5vw, 32px) !important;   /* no media query: Gradio scopes those inside .contain */
  background: var(--wall) !important;
}}
body .gradio-container .main {{ padding: 0 !important; }}

/* ---------- Hero ---------- */
#twin-hero, #twin-hero > div {{ background: transparent !important; border: 0 !important; padding: 0 !important; }}
.hero {{
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 24px;
  padding: 8px 0 32px;
}}
.hero-photo {{ width: 72px; height: 72px; border-radius: 16px; object-fit: cover; display: block; }}
.hero-monogram {{
  display: grid; place-items: center; background: var(--raised); color: var(--ink);
  font-weight: 700; font-size: 24px; letter-spacing: 0.02em;
}}
.hero-name {{ font-size: 40px; line-height: 1.05; font-weight: 700; letter-spacing: -0.02em; margin: 0 0 8px; color: var(--wall-text); }}
.hero-role {{ font-size: 18px; font-weight: 500; margin: 0 0 6px; color: var(--wall-text); }}
.hero-pitch {{ font-size: 16px; line-height: 1.5; margin: 0; color: var(--wall-muted); max-width: 62ch; }}
.hero-links {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: 12px 20px; }}
.hero-links a {{
  display: inline !important; padding: 0 !important;
  color: var(--wall-text); font-weight: 500; text-decoration: underline;
  text-decoration-color: var(--accent); text-underline-offset: 4px; text-decoration-thickness: 1.5px;
}}
.hero-links a:hover {{ color: var(--accent); }}
.hero-links a.hero-cta {{
  display: inline-block !important; padding: 10px 16px !important; border-radius: 12px;
  border: 1.5px solid var(--accent); color: var(--accent); text-decoration: none;
  transition: background-color 150ms ease, color 150ms ease, transform 160ms var(--ease-out);
}}
.hero-links a.hero-cta:hover {{ background: var(--accent); color: var(--on-accent); }}
.hero-links a.hero-cta:active {{ transform: scale(0.97); }}

/* ---------- Two cards on the wall ---------- */
#twin-row {{ gap: 24px; align-items: stretch; }}
#twin-label, #twin-chat-col {{
  background: var(--surface); border: 1px solid var(--card-edge); border-radius: 16px;
}}
#twin-label {{ padding: 20px; }}
.wall-label {{ color: var(--ink); font-size: 16px; line-height: 1.55; }}
.wl-medium {{ font-size: 16px; font-weight: 500; margin: 0 0 8px; color: var(--ink); }}
.wl-meta {{ font-size: 14px; color: var(--muted); margin: 0 0 28px; }}
.wl-heading {{ font-size: 16px; font-weight: 700; margin: 0 0 8px; color: var(--ink); }}
.wl-work {{ list-style: none; margin: 0; padding: 0; }}
.wl-work li {{ padding: 12px 0; border-top: 1px solid var(--line); color: var(--muted); font-size: 14px; }}
.wl-work strong {{ display: block; color: var(--ink); font-weight: 600; font-size: 16px; margin-bottom: 2px; }}
.wl-contact-heading {{ margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--line); }}
.wl-contact {{ font-size: 16px; color: var(--ink); margin: 0; }}
.wall-label a {{
  display: inline !important; padding: 0 !important;
  color: var(--accent-text); font-weight: 500; text-decoration: underline;
  text-underline-offset: 3px; text-decoration-thickness: 1px;
}}
.wall-label a:hover {{ text-decoration-thickness: 2px; }}

/* ---------- The chat card ---------- */
#twin-chat-col {{ padding: 12px 12px 16px; }}
#twin-chat-col > .column {{ height: 100%; }}
#twin-chat {{
  flex: 1 1 0 !important; height: auto !important; min-height: 460px;
  background: transparent !important; border: 0 !important;
}}
#twin-chat .wrapper, #twin-chat .bubble-wrap {{ height: 100% !important; background: transparent !important; }}
#twin-chat .prose {{ font-size: 16px !important; }}
#twin-chat .message-row {{ margin: 6px 0 !important; }}
#twin-chat .message-row .flex-wrap > .message {{
  max-width: 92% !important; border: 0 !important; box-shadow: none !important;
  font-size: 16px !important; line-height: 1.6 !important; padding: 10px 14px !important;
}}
#twin-chat .message-row .message .message, #twin-chat .message-row .message-content {{
  background: transparent !important; border: 0 !important; padding: 0 !important; margin: 0 !important; max-width: none !important;
}}
#twin-chat .user-row .flex-wrap > .message {{
  background: var(--raised) !important; color: var(--ink) !important;
  border: 1px solid var(--line) !important; border-radius: 12px 12px 4px 12px !important;
}}
#twin-chat .bubble.bot-row {{ max-width: 100% !important; align-self: stretch !important; }}
#twin-chat .bot-row .flex-wrap > .message {{
  background: transparent !important; color: var(--ink) !important;
  border-left: 2px solid var(--accent-edge) !important; border-radius: 0 !important; padding-left: 14px !important;
}}

/* Markdown inside replies */
#twin-chat .bot-row .message p {{ margin: 0 0 0.6em; }}
#twin-chat .bot-row .message p:last-child {{ margin-bottom: 0; }}
#twin-chat .bot-row .message ul, #twin-chat .bot-row .message ol {{ list-style-position: outside; margin: 0.3em 0 0.7em 0; padding-left: 1.25em; }}
#twin-chat .bot-row .message li {{ margin: 0.2em 0; }}
#twin-chat .bot-row .message strong {{ font-weight: 600; }}
#twin-chat .bot-row .message a {{ color: var(--accent-text); text-underline-offset: 3px; }}
#twin-chat .bot-row .message a:hover {{ text-decoration-thickness: 2px; }}
#twin-chat .bot-row .message table {{ border-collapse: collapse; margin: 0.6em 0; font-size: 14px; font-variant-numeric: tabular-nums; }}
#twin-chat .bot-row .message th, #twin-chat .bot-row .message td {{ border-bottom: 1px solid var(--line); padding: 6px 10px; text-align: left; }}

/* ---------- Tool steps: one fixed row, the dot pulses amber while it runs ---------- */
#twin-chat .thought-group {{
  background: transparent !important; border: 0 !important; border-radius: 0 !important;
  padding: 2px 0 8px !important; margin: 0 0 6px !important;
  border-bottom: 1px solid var(--line) !important;
}}
#twin-chat .thought-group .title {{
  display: flex; align-items: center; justify-content: flex-start; gap: 8px; width: 100%;
  padding: 0 !important; margin: 0 !important;
}}
#twin-chat .thought-group .title::before {{
  content: ""; flex: none; width: 8px; height: 8px; border-radius: 50%; background: var(--muted);
}}
#twin-chat .thought-group .title[aria-busy="true"]::before {{
  background: var(--accent-edge); animation: twin-live 1.1s var(--ease-out) infinite alternate;   /* 4.3:1 in light mode, so it reads even without the pulse */
}}
@keyframes twin-live {{ from {{ opacity: 1; transform: scale(1); }} to {{ opacity: 0.45; transform: scale(0.8); }} }}
#twin-chat .thought-group .title .arrow {{ order: 3; margin: 0 !important; }}
#twin-chat .thought-group .loading-spinner {{ display: none !important; }}   /* the amber dot already says it's running */
#twin-chat .thought-group .dropdown-arrow .circle {{ fill: transparent !important; }}
#twin-chat .thought-group .dropdown-arrow {{ fill: var(--muted) !important; }}
#twin-chat .thought-group .title .prose {{ flex: 1 1 auto !important; width: auto !important; }}   /* spinner, then duration, keep the right column */
#twin-chat .thought-group .title .prose, #twin-chat .thought-group .title p {{
  font-size: 14px !important; font-weight: 500; color: var(--ink); margin: 0 !important;
}}
#twin-chat .thought-group .title button {{ background: transparent !important; border: 0 !important; padding: 0 !important; color: var(--muted) !important; }}
#twin-chat .thought-group .message-content, #twin-chat .thought-group .message-content .prose {{
  font-size: 14px !important; color: var(--muted) !important; opacity: 1 !important; padding: 4px 0 0 16px !important;
}}
#twin-chat .duration {{ order: 2; margin-left: auto !important; font-size: 14px !important; font-variant-numeric: tabular-nums; color: var(--muted) !important; }}

/* ---------- Empty chat: one invitation, centred in the card ---------- */
#twin-chat .placeholder-content {{ justify-content: center !important; gap: 20px; }}
#twin-chat .placeholder {{ flex: 0 0 auto !important; display: block !important; height: auto !important; }}
#twin-chat .placeholder > .prose {{ width: 100% !important; }}
.chat-start {{ padding: 0; }}
#twin-chat .bubble-wrap {{ padding: 32px 8px 0 !important; }}   /* 8px inset like the composer; 32px clears the clear-chat icon */
.chat-greeting {{
  font-size: 24px; line-height: 1.3; font-weight: 600; color: var(--ink); margin: 0 0 16px;
  border-left: 2px solid var(--accent-edge); padding-left: 14px; max-width: 30ch;
}}
.chat-how {{ list-style: none; margin: 0; padding: 0 0 0 16px; max-width: 60ch; }}
.chat-how li {{
  position: relative; padding: 0 0 8px 18px; margin: 0;
  font-size: 14px; line-height: 1.5; color: var(--muted);
}}
.chat-how li::before {{
  content: ""; position: absolute; left: 0; top: 0.55em; width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
}}
.chat-how strong {{ color: var(--ink); font-weight: 600; }}

/* ---------- Starter chips ---------- */
#twin-chat .examples {{
  display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 10px !important;
  padding: 0 !important; margin: 0 !important; max-width: none !important;
}}
#twin-chat .example {{
  background: var(--raised) !important; border: 1px solid var(--line) !important; border-radius: 12px !important;
  padding: 12px 14px !important; color: var(--ink) !important; box-shadow: none !important;
  transition: border-color 150ms ease, transform 150ms var(--ease-out) !important;
}}
#twin-chat .example-content {{ display: flex !important; flex-direction: row !important; align-items: center !important; gap: 10px !important; }}
#twin-chat .example-content::before {{
  content: ""; flex: none; width: 16px; height: 16px; background-color: var(--muted);
  -webkit-mask: center / contain no-repeat; mask: center / contain no-repeat;
  transition: background-color 150ms ease;
}}
{chip_icon_rules}
#twin-chat .example-text-content {{ margin: 0 !important; }}
#twin-chat .example-text {{ color: var(--ink) !important; font-size: 15px !important; font-weight: 500; line-height: 1.4; white-space: normal; }}
#twin-chat .example:active {{ transform: scale(0.98) !important; }}
@media (hover: hover) and (pointer: fine) {{
  #twin-chat .example:hover {{ border-color: var(--accent-edge) !important; background: var(--raised) !important; transform: translateY(-1px) !important; }}
  #twin-chat .example:hover .example-content::before {{ background-color: var(--accent-edge); }}
}}

/* ---------- Composer ---------- */
#twin-chat-col .gr-group, #twin-chat-col .styler, #twin-chat-col .form, #twin-input .wrap {{
  background: transparent !important; border: 0 !important; box-shadow: none !important;
}}
#twin-input {{ background: transparent !important; border: 0 !important; box-shadow: none !important; padding: 12px 8px 0 !important; }}
#twin-input .input-container {{ gap: 8px; align-items: flex-end; }}
#twin-input textarea {{
  min-height: 52px !important; padding: 14px 16px !important; font-size: 16px !important;
  border: 1px solid var(--control-edge) !important; border-radius: 12px !important;
  background: var(--raised) !important; color: var(--ink) !important; box-shadow: none !important;
  transition: border-color 150ms ease, box-shadow 150ms ease !important;
}}
#twin-input textarea:focus {{
  border-color: var(--accent-edge) !important; outline: none !important;
  box-shadow: 0 0 0 3px rgba(227, 167, 47, 0.25) !important;
}}
#twin-input .submit-button, #twin-input .stop-button {{
  background: var(--accent) !important; color: var(--on-accent) !important; border: 0 !important; border-radius: 12px !important;
  width: 52px !important; height: 52px !important; min-width: 52px !important; margin: 0 !important;
  transition: transform 160ms var(--ease-out), background-color 150ms ease !important;
}}
#twin-input .submit-button:hover, #twin-input .stop-button:hover {{ background: var(--accent-hover) !important; }}
#twin-input .submit-button:active, #twin-input .stop-button:active {{ transform: scale(0.97); }}
#twin-input .submit-button svg *, #twin-input .stop-button svg * {{ stroke: var(--on-accent) !important; fill: var(--on-accent) !important; }}

/* ---------- Small chat icons (copy, retry, undo) ---------- */
#twin-chat button[aria-label]:not(.example), #twin-chat .icon-button {{
  color: var(--muted) !important; background: transparent !important; border: 0 !important; border-radius: 8px !important;
}}
#twin-chat .icon-button-wrapper {{ background: transparent !important; border: 0 !important; box-shadow: none !important; }}
#twin-chat button[aria-label]:not(.example):hover, #twin-chat .icon-button:hover {{ color: var(--accent-text) !important; }}

/* ---------- Browser surfaces ---------- */
::selection {{ background: rgba(227, 167, 47, 0.3); }}
:focus-visible {{ outline: 2px solid var(--accent-edge) !important; outline-offset: 2px; }}
#twin-chat ::-webkit-scrollbar {{ width: 8px; }}
#twin-chat ::-webkit-scrollbar-thumb {{ background: var(--line); border-radius: 8px; }}
textarea {{ caret-color: var(--accent-edge); }}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition-duration: 0ms !important; }}
}}

/* ---------- Phone: hero stacks, the chat comes first after it ---------- */
@media (max-width: 760px) {{
  .hero {{ grid-template-columns: auto 1fr; gap: 12px 16px; padding: 4px 0 20px; }}
  .hero-photo {{ width: 56px; height: 56px; border-radius: 14px; }}
  .hero-name {{ font-size: 28px; margin-bottom: 4px; }}
  .hero-role {{ font-size: 16px; }}
  .hero-pitch {{ display: none; }}
  .hero-links {{ grid-column: 1 / -1; justify-content: flex-start; }}
  #twin-row {{ gap: 12px; }}
  #twin-chat-col {{ order: -1; }}   /* on a phone the chat comes straight after the hero */
  #twin-label {{ padding: 16px; }}
  .wl-meta {{ margin-bottom: 14px; }}
  .wl-work li {{ padding: 6px 0; }}
  #twin-chat .message-row .flex-wrap > .message {{ max-width: 100% !important; }}
  #twin-chat .bot-row .flex-wrap {{ width: 100% !important; }}
  #twin-chat {{ flex: none !important; height: 72vh !important; min-height: 0; }}
  #twin-chat:has(.placeholder) {{ height: auto !important; }}
  #twin-chat:has(.placeholder) .wrapper, #twin-chat:has(.placeholder) .bubble-wrap {{ height: auto !important; }}
  #twin-chat .examples {{ grid-template-columns: 1fr !important; padding: 0 !important; }}
  .chat-start {{ padding: 0; }}
  .chat-greeting {{ font-size: 20px; }}
  .chat-how {{ display: none; }}
}}
"""

JS = """
() => {
  const watch = (area) => {
    if (area.dataset.twinWatched) return;
    area.dataset.twinWatched = '1';
    const hint = area.placeholder;
    let was = area.disabled || area.readOnly;
    new MutationObserver(() => {
      const now = area.disabled || area.readOnly;
      if (was && !now) area.focus({ preventScroll: true });   // back to the composer after each reply
      if (!area.placeholder && hint) area.placeholder = hint;   // Gradio blanks it after the first message
      was = now;
    }).observe(area, { attributes: true, attributeFilter: ['disabled', 'readonly', 'placeholder'] });
  };
  const scan = () => document.querySelectorAll('#twin-input textarea').forEach(watch);
  setTimeout(scan, 500);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
}
"""

# Gradio 6.14 doesn't run launch(js=...) here, so the script goes in the page head instead.
# Gradio adds the head after the page has loaded, so run it straight away if that has already happened.
HEAD = (
    "<script>(() => { const run = " + JS.strip() + ";"
    " if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run(); })();</script>"
)
