"""
Streamlit frontend for the AI Research Agent.

This file only adds a UI layer. It reuses the exact same building blocks the
command-line pipeline (pipeline.py) uses — search_web_agent, scrape_web_agent,
summary_chain and critic_chain from agent.py — so behaviour stays identical
while the interface can show each stage of the agent as it runs.

Run with:  streamlit run app.py
"""

import re
from datetime import datetime

import streamlit as st

# Same components the CLI pipeline uses. Importing agent.py also runs
# load_dotenv(), so MISTRAL_API_KEY / TAVILY_API_KEY are loaded from .env.
from agent import (
    search_web_agent,
    scrape_web_agent,
    summary_chain,
    critic_chain,
)

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Atlas · Research Agent",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# Theme — grainy ink canvas, editorial serif
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
      :root {
        --bg:      #0A0A0C;
        --text:    #F4F2ED;   /* warm white          */
        --muted:   #7C7C82;
        --faint:   #4A4A50;
        --line:    rgba(255,255,255,0.09);
        --panel:   rgba(255,255,255,0.035);
        --panel-l: rgba(255,255,255,0.08);
        --signal:  #D9A066;   /* lone warm gold — functional only */
      }

      /* Grainy, light-bled canvas */
      .stApp {
        color: var(--text);
        background:
          radial-gradient(1100px 560px at 12% -12%, rgba(255,255,255,0.07), transparent 60%),
          radial-gradient(900px 500px at 102% 112%, rgba(255,255,255,0.06), transparent 60%),
          var(--bg);
      }
      .stApp::before {
        content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
        opacity: 0.05; mix-blend-mode: screen;
      }

      html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; color: var(--text); }

      /* Strip Streamlit chrome + the whole sidebar */
      #MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; }
      section[data-testid="stSidebar"],
      [data-testid="stSidebarCollapsedControl"] { display: none !important; }

      .block-container { position: relative; z-index: 1; padding-top: 1.4rem; max-width: 760px; }

      /* ── Top bar ─────────────────────────────────────────────────── */
      .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding-bottom: 2.4rem;
      }
      .brand { font-family: 'Instrument Serif', serif; font-size: 1.5rem; letter-spacing: 0.01em; }
      .brand .acc { color: var(--signal); }
      .status {
        display: inline-flex; align-items: center; gap: 0.45rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
        color: var(--muted); padding: 0.32rem 0.7rem;
        border: 1px solid var(--line); border-radius: 999px;
      }
      .status .dot { width: 6px; height: 6px; border-radius: 50%; }
      .status .ok  { background: #6FCF97; }
      .status .bad { background: #E06A6A; }

      /* ── Hero ────────────────────────────────────────────────────── */
      .hero { text-align: center; margin: 1.4rem 0 2.2rem; }
      .badge {
        display: inline-flex; align-items: center; gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.66rem;
        letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted);
        padding: 0.35rem 0.9rem; border: 1px solid var(--line); border-radius: 999px;
        margin-bottom: 1.6rem;
      }
      .badge .g { color: var(--signal); }
      .display {
        font-family: 'Instrument Serif', serif; font-weight: 400;
        font-size: clamp(2.8rem, 6vw, 4.4rem); line-height: 1.02;
        letter-spacing: -0.01em; margin: 0;
      }
      .display em { font-style: italic; color: var(--text); }
      .sub {
        color: var(--muted); font-size: 1.05rem; line-height: 1.6;
        max-width: 100%; margin: 1.3rem auto 0;
      }

      /* ── Inputs ──────────────────────────────────────────────────── */
      .stTextInput input {
        background: var(--panel) !important; color: var(--text) !important;
        border: 1px solid var(--panel-l) !important; border-radius: 14px !important;
        font-family: 'Inter', sans-serif !important; font-size: 1.02rem !important;
        padding: 0.95rem 1.1rem !important;
      }
      .stTextInput input::placeholder { color: var(--faint) !important; }
      .stTextInput input:focus { border-color: var(--signal) !important; box-shadow: none !important; }

      /* Primary action — warm-white pill */
      .stButton button[kind="primary"] {
        background: var(--text); color: #111; border: none;
        border-radius: 14px; font-weight: 600; font-family: 'Inter', sans-serif;
        height: 100%; min-height: 3.25rem; padding: 0 1.1rem;
        transition: transform .08s ease, filter .15s ease;
      }
      .stButton button[kind="primary"]:hover { filter: brightness(0.92); transform: translateY(-1px); }
      .stButton button[kind="primary"]:active { transform: translateY(0); }

      /* Chips — ghost pills */
      .stButton button[kind="secondary"] {
        background: transparent; color: var(--muted);
        border: 1px solid var(--line); border-radius: 999px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
        padding: 0.4rem 0.9rem; transition: color .15s ease, border-color .15s ease;
      }
      .stButton button[kind="secondary"]:hover { color: var(--text); border-color: var(--panel-l); }

      /* Download — quiet outline */
      [data-testid="stDownloadButton"] button {
        background: transparent; color: var(--muted);
        border: 1px solid var(--line); border-radius: 999px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
      }
      [data-testid="stDownloadButton"] button:hover { color: var(--text); border-color: var(--panel-l); }

      /* ── Stage trace ─────────────────────────────────────────────── */
      .stage {
        display: flex; align-items: center; gap: 0.8rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.84rem;
        padding: 0.55rem 0; border-bottom: 1px dashed var(--line); color: var(--muted);
      }
      .stage .num { color: var(--faint); width: 2.4rem; }
      .stage.active { color: var(--text); }
      .stage.active .num, .stage.done .num { color: var(--signal); }

      /* ── Report surfaces ─────────────────────────────────────────── */
      .panel { background: var(--panel); border: 1px solid var(--panel-l); border-radius: 16px; padding: 1.6rem 1.8rem; }
      .panel-title {
        font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
        letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted);
        margin-bottom: 1rem;
      }
      .gauge { background: var(--panel); border: 1px solid var(--panel-l); border-radius: 16px; padding: 1.4rem 1.6rem; text-align: center; }
      .gauge .val { font-family: 'Instrument Serif', serif; font-size: 3.6rem; line-height: 1; color: var(--signal); }
      .gauge .val small { font-size: 1.2rem; color: var(--muted); }
      .gauge .lbl {
        font-family: 'JetBrains Mono', monospace; font-size: 0.66rem;
        letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); margin-top: 0.5rem;
      }

      [data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--panel-l); border-radius: 14px; }

      a { color: var(--text); text-decoration: underline; text-underline-offset: 3px; }

      @media (prefers-reduced-motion: reduce) {
        .stButton button { transition: none !important; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def keys_present() -> dict:
    import os

    return {
        "MISTRAL_API_KEY": bool(os.getenv("MISTRAL_API_KEY")),
        "TAVILY_API_KEY": bool(os.getenv("TAVILY_API_KEY")),
    }


def parse_score(critic_text: str):
    """Pull 'Score: X/10' out of the critic response, if present."""
    m = re.search(r"Score:\s*([\d.]+)\s*/\s*10", critic_text or "", re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def run_research(topic: str, trace_box, on_stage):
    """
    Re-runs the same four steps as pipeline.research_pipeline, but surfaces
    each stage to the UI as it completes. Returns the same state dict shape.
    """
    state = {}

    # Stage 1 — web search
    on_stage(0, "active")
    search_agent = search_web_agent()
    search_results = search_agent.invoke(
        {"messages": [("user", f"Find reliable and relevant information about the topic {topic}")]}
    )
    state["search_results"] = search_results["messages"][-1].content
    on_stage(0, "done")

    # Stage 2 — scrape best source
    on_stage(1, "active")
    reader_agent = scrape_web_agent()
    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}",
                )
            ]
        }
    )
    state["reader_result"] = reader_result["messages"][-1].content
    on_stage(1, "done")

    # Stage 3 — synthesize report
    on_stage(2, "active")
    research_total = (
        f"Search results : {state['search_results']}"
        f" Scraped content : {state['reader_result']}"
    )
    state["summary_result"] = summary_chain.invoke(
        {"topic": topic, "research": research_total}
    )
    on_stage(2, "done")

    # Stage 4 — critique
    on_stage(3, "active")
    state["critic_result"] = critic_chain.invoke({"report": state["summary_result"]})
    on_stage(3, "done")

    return state


STAGES = [
    ("01", "SEARCH", "Querying the open web for sources"),
    ("02", "SCRAPE", "Reading the most relevant source in depth"),
    ("03", "SYNTHESIZE", "Writing a structured research report"),
    ("04", "CRITIQUE", "Grading the report for rigor"),
]


def render_trace(container, statuses):
    rows = []
    for i, (num, name, desc) in enumerate(STAGES):
        s = statuses[i]
        glyph = {"idle": "○", "active": "◐", "done": "●"}[s]
        cls = "stage done" if s == "done" else ("stage active" if s == "active" else "stage")
        label = f"{name} — {desc}" if s != "idle" else f"{name}"
        rows.append(
            f'<div class="{cls}"><span class="num">{num}</span>'
            f'<span>{glyph}</span><span>{label}</span></div>'
        )
    container.markdown("".join(rows), unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Top bar — brand only (sidebar removed)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="topbar">
      <div class="brand">Atlas<span class="acc">.</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
      <h1 class="display">Ask anything.<br><em>Atlas does the reading.</em></h1>
      <p class="sub">It searches the open web, reads the best source in depth,
      writes a structured report — then grades its own work, and shows you every step.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Session state
if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.topic = None
    st.session_state.ran_at = None

# ── Input ─────────────────────────────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1.4])
with col_in:
    topic = st.text_input(
        "Research topic",
        placeholder="What should Atlas research?",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("Research →", type="primary", use_container_width=True)

missing = [k for k, ok in keys_present().items() if not ok]

# Resolve which topic (if any) to research this run
topic_to_run = None
if run:
    if topic and topic.strip():
        topic_to_run = topic.strip()
    else:
        st.warning("Enter a topic to research.")

# ── Run ───────────────────────────────────────────────────────────────────────
if topic_to_run:
    if missing:
        st.error(
            "Can't start — these API keys aren't loaded: "
            + ", ".join(missing)
            + ". Add them to your .env file and restart."
        )
    else:
        statuses = ["idle"] * len(STAGES)
        st.markdown('<div class="panel-title" style="margin-top:1.8rem">Agent trace</div>',
                    unsafe_allow_html=True)
        trace = st.empty()
        render_trace(trace, statuses)

        def on_stage(i, s):
            statuses[i] = s
            render_trace(trace, statuses)

        try:
            with st.spinner("Agent working…"):
                result = run_research(topic_to_run, trace, on_stage)
            st.session_state.result = result
            st.session_state.topic = topic_to_run
            st.session_state.ran_at = datetime.now().strftime("%b %d, %Y · %H:%M")
        except Exception as e:  # surface real failures instead of a blank screen
            st.error(f"The agent hit an error: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
res = st.session_state.result
if res:
    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='color:var(--muted);font-family:JetBrains Mono;font-size:0.78rem;'>"
        f"TOPIC · {st.session_state.topic}  —  {st.session_state.ran_at}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    report = res.get("summary_result", "")
    critic = res.get("critic_result", "")
    score = parse_score(critic)

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown('<div class="panel-title">Research report</div>', unsafe_allow_html=True)
        st.markdown(report or "_No report generated._")
        if report:
            st.download_button(
                "Download report (.md)",
                data=f"# {st.session_state.topic}\n\n{report}\n\n---\n\n## Critique\n\n{critic}",
                file_name=f"atlas_report_{st.session_state.topic[:30].replace(' ', '_')}.md",
                mime="text/markdown",
            )

    with right:
        if score is not None:
            st.markdown(
                f'<div class="gauge"><div class="val">{score:g}<small>/10</small></div>'
                f'<div class="lbl">Critic score</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Critique</div>', unsafe_allow_html=True)
        st.markdown(critic or "_No critique generated._")

    # Raw research material, tucked away
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    with st.expander("Sources & raw research"):
        st.markdown("**Web search results**")
        st.text(res.get("search_results", "—"))
        st.markdown("**Scraped content**")
        st.text(res.get("reader_result", "—"))

else:
    # Empty state — an invitation, not a void
    st.markdown(
        """
        <div class="panel" style="margin-top:1.6rem;border-style:dashed;">
          <div class="panel-title">Ready</div>
          <div style="color:var(--muted);">
            Enter a topic above and the agent runs four stages end to end —
            you'll watch each one light up as it works, then get a sourced report
            with a critic's score.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
