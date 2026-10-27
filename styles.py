"""Styling for the digital-twin Gradio app.

Usage
-----
    from styles import THEME, CSS, JS, EXAMPLES, HEADER_HTML, PLACEHOLDER_HTML

See app.py: the ChatInterface is wrapped in gr.Blocks so a branded header
can sit above it; THEME / CSS / JS are passed to demo.launch() (Gradio 6).

Design notes
------------
* Direction: "Spark"-style glass-dark (translucent surfaces over a brand glow,
  12–16px radii, 16px chat text) with a Citrus-style pressed-key send button.
  Gold is the only saturated color; blue is a translucent user bubble, purple a
  hairline stripe on assistant rows.
* Everything neutral is driven by Gradio's theme tokens so dark/light mode works
  without CSS hacks.
* We target our own `elem_id`s (#twin-chat, #twin-input) plus the handful of
  Gradio Chatbot classes that have been stable across 4.x/5.x
  (.message-row, .user-row, .bot-row, .message). Nothing deeper.
* No blanket `* { background: transparent; color: inherit }` inside bubbles —
  that rule was nuking code blocks, tables and lists that an agent produces.
"""

from __future__ import annotations

import gradio as gr
from gradio.themes.utils import colors, fonts, sizes

GOLD = "#ecad0a"
GOLD_HOVER = "#f5bf2a"
BLUE = "#209dd7"
PURPLE = "#753991"

EXAMPLES = [
    "Tell me about your background and experience.",
    "What kinds of projects are you working on now?",
    "What are your strongest technical skills?",
    "How can I get in touch with you?",
]

# --------------------------------------------------------------------------- #
# Theme: handles fonts, radii, neutrals, and dark/light switching natively.
# --------------------------------------------------------------------------- #
THEME = gr.themes.Base(
    primary_hue=colors.Color(
        name="twin-gold",
        c50="#fff9e6", c100="#ffefbf", c200="#ffe28a", c300="#fdd35a",
        c400="#f5c22e", c500=GOLD, c600="#c98f06", c700="#a27204",
        c800="#7a5503", c900="#523902", c950="#2e2001",
    ),
    secondary_hue=colors.sky,
    neutral_hue=colors.zinc,
    spacing_size=sizes.spacing_md,
    radius_size=sizes.radius_lg,          # 12px blocks / composer (Spark-style)
    text_size=sizes.text_md,
    font=(fonts.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"),
    font_mono=(fonts.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"),
).set(
    # Page
    body_background_fill="#f6f6f8",
    body_background_fill_dark="#0b0b0e",
    body_text_color="#1a1a20",
    body_text_color_dark="#ececef",
    body_text_color_subdued="#6a6a72",
    body_text_color_subdued_dark="#8c8c95",
    link_text_color=BLUE,
    link_text_color_dark=GOLD,
    # Blocks / surfaces — translucent so the brand glow shows through
    block_background_fill="rgba(255,255,255,0.72)",
    block_background_fill_dark="rgba(255,255,255,0.045)",
    block_border_color="rgba(0,0,0,0.08)",
    block_border_color_dark="rgba(255,255,255,0.08)",
    block_border_width="1px",
    block_shadow="0 4px 24px rgba(0,0,0,0.06)",
    block_shadow_dark="0 4px 24px rgba(0,0,0,0.35)",
    block_label_text_color="#6a6a72",
    block_label_text_color_dark="#8c8c95",
    background_fill_secondary="rgba(0,0,0,0.04)",
    background_fill_secondary_dark="rgba(255,255,255,0.06)",
    border_color_primary="rgba(0,0,0,0.08)",
    border_color_primary_dark="rgba(255,255,255,0.08)",
    color_accent=GOLD,
    color_accent_soft="rgba(236,173,10,0.12)",
    color_accent_soft_dark="rgba(236,173,10,0.16)",
    # Inputs
    input_background_fill="rgba(255,255,255,0.85)",
    input_background_fill_dark="rgba(255,255,255,0.05)",
    input_border_color="rgba(0,0,0,0.10)",
    input_border_color_dark="rgba(255,255,255,0.08)",
    input_border_color_focus=GOLD,
    input_border_color_focus_dark=GOLD,
    input_shadow_focus="0 0 0 3px rgba(236,173,10,0.20)",
    input_placeholder_color="#9a9aa3",
    input_placeholder_color_dark="#6e6e78",
    # Buttons — gold is the only saturated element; Citrus-style press on primary
    button_border_width="0px",
    button_primary_background_fill=GOLD,
    button_primary_background_fill_hover=GOLD_HOVER,
    button_primary_text_color="#111111",
    button_primary_shadow="0 3px 0 0 #a27204",
    button_primary_shadow_hover="0 5px 0 0 #a27204",
    button_primary_shadow_active="0 1px 0 0 #a27204",
    button_transform_hover="translateY(-2px)",
    button_transform_active="translateY(2px)",
    button_transition="all 0.1s ease",
    button_secondary_background_fill="rgba(0,0,0,0.04)",
    button_secondary_background_fill_dark="rgba(255,255,255,0.08)",
    button_secondary_background_fill_hover="rgba(0,0,0,0.07)",
    button_secondary_background_fill_hover_dark="rgba(255,255,255,0.12)",
    button_secondary_text_color="#1a1a20",
    button_secondary_text_color_dark="#ececef",
    button_secondary_shadow="none",
    button_secondary_shadow_hover="none",
    button_large_radius="*radius_lg",
    button_small_radius="*radius_md",
    # Chatbot
    chatbot_text_size="*text_lg",
)

# --------------------------------------------------------------------------- #
# Optional branded header. Drop into gr.HTML(HEADER_HTML) above the chat.
# --------------------------------------------------------------------------- #
HEADER_HTML = """
<header class="twin-header">
  <div class="twin-eyebrow">
    <span class="twin-dot"></span> DIGITAL TWIN · ONLINE
  </div>
  <h1 class="twin-title">Ask my career twin</h1>
  <p class="twin-sub">An AI agent trained on my experience, projects and skills.
     Ask it anything a recruiter or collaborator would.</p>
</header>
"""

PLACEHOLDER_HTML = """
<div class="twin-placeholder">
  <div class="twin-placeholder-mark">✦</div>
  <strong>Start a conversation</strong>
  <span>Pick an example below or type a question.</span>
</div>
"""

CSS = """
/* ====================================================================== */
/*  Tokens – accents only. Neutrals come from the Gradio theme above.      */
/* ====================================================================== */
:root {
  --twin-gold:   #ecad0a;
  --twin-blue:   #209dd7;
  --twin-purple: #753991;
  --twin-ease:   cubic-bezier(.2,.8,.2,1);
}

/* Hide Gradio chrome */
footer, .built-with, .show-api, .api-docs { display: none !important; }

/* ---------- Page shell ---------- */
.gradio-container {
  max-width: 860px !important;
  margin: 0 auto !important;
  padding: 40px 24px 56px !important;
  position: relative;
}
/* Soft brand glow behind the page – subtle depth without gradients on UI */
body::before {
  content: "";
  position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background:
    radial-gradient(60% 40% at 20% 0%,  rgba(32,157,215,.10), transparent 70%),
    radial-gradient(50% 35% at 85% 10%, rgba(117,57,145,.10), transparent 70%);
}
.dark body::before, body.dark::before {
  background:
    radial-gradient(60% 45% at 20% 0%,  rgba(32,157,215,.20), transparent 70%),
    radial-gradient(55% 40% at 85% 10%, rgba(117,57,145,.22), transparent 70%),
    radial-gradient(40% 30% at 50% 100%, rgba(236,173,10,.07), transparent 70%);
}

/* ---------- Header ---------- */
.twin-header { margin: 0 0 22px; }
.twin-eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-mono);
  font-size: 11px; letter-spacing: .14em; font-weight: 600;
  color: var(--body-text-color-subdued);
  margin-bottom: 10px;
}
.twin-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--twin-gold);
  box-shadow: 0 0 0 0 rgba(236,173,10,.6);
  animation: twin-pulse 2.2s infinite;
}
@keyframes twin-pulse {
  0%   { box-shadow: 0 0 0 0   rgba(236,173,10,.55); }
  70%  { box-shadow: 0 0 0 8px rgba(236,173,10,0); }
  100% { box-shadow: 0 0 0 0   rgba(236,173,10,0); }
}
.twin-title {
  font-size: clamp(26px, 4vw, 34px);
  font-weight: 700; letter-spacing: -0.025em; line-height: 1.1;
  margin: 0 0 8px;
  color: var(--body-text-color);
}
.twin-sub {
  margin: 0; max-width: 56ch;
  font-size: 15px; line-height: 1.55;
  color: var(--body-text-color-subdued);
}

/* ---------- Chat frame ---------- */
#twin-chat {
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 16px !important;
  background: var(--block-background-fill) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--block-shadow);
  overflow: hidden;
}
#twin-chat .placeholder { background: transparent !important; }
.twin-placeholder {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  text-align: center; color: var(--body-text-color-subdued);
  padding: 48px 16px;
}
.twin-placeholder-mark { font-size: 28px; color: var(--twin-gold); line-height: 1; margin-bottom: 6px; }
.twin-placeholder strong { color: var(--body-text-color); font-weight: 600; }

/* ---------- Message rows ----------
   Gradio 6 DOM:  .message-row > .flex-wrap.role > .{user|bot}.message > .message.panel-full-width > …
   Style the OUTER .message only; the inner one is flattened. */
#twin-chat .message-row { margin: 6px 0 !important; }
#twin-chat .message-row:first-child { margin-top: 36px !important; }   /* clear the share/clear toolbar */
#twin-chat .user-row { padding-right: 10px !important; }
#twin-chat .message-row .flex-wrap > .message {
  max-width: 78% !important;                /* iMessage-style width, not full-bleed */
  padding: 11px 15px !important;
  border: 0 !important;
  box-shadow: none !important;
  font-size: 16px !important;
  line-height: 1.6 !important;
  animation: twin-rise .22s var(--twin-ease) both;
}
#twin-chat .message-row .message .message,
#twin-chat .message-row .message-content {
  max-width: none !important;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 0 !important;
}
@keyframes twin-rise { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

/* User: translucent brand blue + blue hairline, so gold stays the only loud color */
#twin-chat .user-row .flex-wrap > .message {
  background: rgba(32,157,215,0.16) !important;
  border: 1px solid rgba(32,157,215,0.45) !important;
  color: var(--body-text-color) !important;
  border-radius: 16px 16px 4px 16px !important;
}
/* Assistant: neutral glass + single purple stripe on the ROW (one element, no nesting hacks) */
#twin-chat .bot-row {
  border-left: 2px solid var(--twin-purple);
  padding-left: 10px !important;
}
#twin-chat .bot-row .flex-wrap > .message {
  background: var(--background-fill-secondary) !important;
  color: var(--body-text-color) !important;
  border-radius: 4px 16px 16px 16px !important;
}

/* ---------- Markdown inside assistant bubbles (agents produce this a lot) ---------- */
#twin-chat .bot-row .message p { margin: 0 0 .6em; }
#twin-chat .bot-row .message p:last-child { margin-bottom: 0; }
#twin-chat .bot-row .message ul,
#twin-chat .bot-row .message ol { margin: .4em 0 .6em 1.2em; padding: 0; }
#twin-chat .bot-row .message li { margin: .2em 0; }
#twin-chat .bot-row .message strong { font-weight: 600; color: var(--body-text-color); }
#twin-chat .bot-row .message a { color: var(--twin-blue); text-decoration: underline; text-underline-offset: 2px; }
.dark #twin-chat .bot-row .message a, body.dark #twin-chat .bot-row .message a { color: var(--twin-gold); }
#twin-chat .bot-row .message code {
  font-family: var(--font-mono); font-size: .88em;
  background: rgba(127,127,140,.14); padding: .1em .4em; border-radius: 4px;
}
#twin-chat .bot-row .message pre {
  background: #0f0f13; color: #e6e6ea;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 8px; padding: 12px 14px; margin: .6em 0;
  overflow-x: auto;
}
#twin-chat .bot-row .message pre code { background: transparent; padding: 0; font-size: 13px; }
#twin-chat .bot-row .message table { border-collapse: collapse; margin: .6em 0; font-size: 14px; }
#twin-chat .bot-row .message th,
#twin-chat .bot-row .message td { border: 1px solid var(--border-color-primary); padding: 6px 10px; }
#twin-chat .bot-row .message th { background: rgba(127,127,140,.10); font-weight: 600; }
#twin-chat .bot-row .message hr { border: 0; border-top: 1px solid var(--border-color-primary); margin: .8em 0; }
#twin-chat .bot-row .message blockquote {
  margin: .6em 0; padding: 2px 12px;
  border-left: 3px solid var(--twin-gold); color: var(--body-text-color-subdued);
}

/* ---------- Composer ---------- */
#twin-input {
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 14px !important;
  background: var(--block-background-fill) !important;
  box-shadow: var(--block-shadow) !important;
  transition: border-color .15s var(--twin-ease), box-shadow .15s var(--twin-ease);
}
#twin-input:focus-within {
  border-color: var(--twin-gold) !important;
  box-shadow: 0 0 0 3px rgba(236,173,10,.18) !important;
}
#twin-input textarea {
  min-height: 52px !important;
  padding: 14px 16px !important;
  font-size: 16px !important;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  border-radius: 12px !important;
}
#twin-input textarea:focus { box-shadow: none !important; border: 0 !important; }
/* Send button: gold, Citrus-style "pressed key". Gradio 6's submit button
   has no .primary class, so the theme tokens don't reach it — style it directly. */
#twin-input .submit-button, .submit-button {
  background: var(--twin-gold) !important;
  color: #111 !important;
  border: 0 !important;
  border-radius: 12px !important;
  width: 50px !important; height: 46px !important;
  margin: 3px 4px 6px 4px !important;       /* room for the 3px press shadow */
  box-shadow: 0 3px 0 0 #a27204 !important;
  transition: transform .1s ease, box-shadow .1s ease, background .15s ease !important;
  display: inline-flex !important; align-items: center !important; justify-content: center !important;
}
.submit-button:hover  { background: #f5bf2a !important; transform: translateY(-2px); box-shadow: 0 5px 0 0 #a27204 !important; }
.submit-button:active { transform: translateY(2px);  box-shadow: 0 1px 0 0 #a27204 !important; }
.submit-button svg { width: 20px !important; height: 20px !important; }
.submit-button svg * { stroke: #111 !important; fill: #111 !important; }
#twin-input textarea { padding-right: 64px !important; }

/* ---------- Example chips ---------- */
.examples, [data-testid="examples"] { margin-top: 14px !important; background: transparent !important; }
.examples .label, [data-testid="examples"] .label { display: none !important; }
.examples button, [data-testid="examples"] button {
  background: var(--button-secondary-background-fill) !important;
  border: 1px solid var(--border-color-primary) !important;
  border-radius: 999px !important;
  color: var(--body-text-color) !important;
  font-size: 13.5px !important; font-weight: 500 !important;
  text-transform: none !important; letter-spacing: 0 !important;
  padding: 8px 14px !important; min-height: 0 !important;
  transition: border-color .15s var(--twin-ease), transform .15s var(--twin-ease), background .15s var(--twin-ease);
}
.examples button:hover, [data-testid="examples"] button:hover {
  border-color: var(--twin-blue) !important;
  color: var(--twin-blue) !important;
  transform: translateY(-1px);
}

/* ---------- Icon buttons (copy / retry / undo / clear) ---------- */
#twin-chat .icon-button, #twin-chat button[aria-label] {
  color: var(--body-text-color-subdued) !important;
  background: transparent !important; border: 0 !important;
  min-height: 0 !important; padding: 4px !important;
  border-radius: 6px !important;
}
#twin-chat .icon-button:hover, #twin-chat button[aria-label]:hover {
  color: var(--twin-gold) !important;
  background: rgba(236,173,10,.10) !important;
}

/* ---------- Scrollbar / selection ---------- */
#twin-chat ::-webkit-scrollbar { width: 8px; }
#twin-chat ::-webkit-scrollbar-thumb { background: var(--border-color-primary); border-radius: 8px; }
#twin-chat ::-webkit-scrollbar-thumb:hover { background: var(--twin-purple); }
::selection { background: rgba(236,173,10,.35); }

/* ---------- Accessibility ---------- */
:focus-visible { outline: 2px solid var(--twin-gold); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}

/* ---------- Mobile ---------- */
@media (max-width: 640px) {
  .gradio-container { padding: 24px 14px 40px !important; }
  #twin-chat .message-row .message { max-width: 92% !important; }
  .examples button, [data-testid="examples"] button { font-size: 13px !important; }
}
"""

JS = """
() => {
  document.title = 'Digital Twin';

  const focusInput = () => {
    const area = document.querySelector('#twin-input textarea')
             || [...document.querySelectorAll('textarea')].pop();
    if (area) area.focus();
  };
  setTimeout(focusInput, 300);

  // Re-focus the composer when Gradio re-enables it after a response.
  const watch = (area) => {
    if (area.dataset.twinWatched) return;
    area.dataset.twinWatched = '1';
    let was = area.disabled || area.readOnly;
    new MutationObserver(() => {
      const now = area.disabled || area.readOnly;
      if (was && !now) area.focus();
      was = now;
    }).observe(area, { attributes: true, attributeFilter: ['disabled', 'readonly'] });
  };
  const scan = () => document.querySelectorAll('textarea').forEach(watch);
  setTimeout(scan, 500);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
}
"""