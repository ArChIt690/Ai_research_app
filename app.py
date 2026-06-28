"""
Streamlit frontend for the AI Research Agent.

This file only adds a UI layer. It reuses the exact same building blocks the
command-line pipeline (pipeline.py) uses — search_web_agent, scrape_web_agent,
summary_chain and critic_chain from agent.py — so behaviour stays identical
while the interface can show each stage of the agent as it runs.

Run with:  streamlit run app.py
"""

import re
import time
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
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Theme — deep-ink research console
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
      :root {
        --ink:      #0E1116;
        --surface:  #161B22;
        --surface2: #1B2129;
        --line:     #222B36;
        --text:     #E6EDF3;
        --muted:    #8B98A5;
        --signal:   #FFB454;   /* agent-active amber */
        --cool:     #5AC8FA;   /* critic / score     */
        --good:     #54D6A0;
      }

      .stApp { background: var(--ink); color: var(--text); }

      /* Base type */
      html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif;
        color: var(--text);
      }

      /* Kill default Streamlit chrome we don't want */
      #MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; }
      .block-container { padding-top: 2.2rem; max-width: 1080px; }

      h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.01em; }

      /* ── Masthead ───────────────────────────────────────────────── */
      .masthead { border-bottom: 1px solid var(--line); padding-bottom: 1.4rem; margin-bottom: 1.8rem; }
      .eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; letter-spacing: 0.32em; text-transform: uppercase;
        color: var(--signal); margin-bottom: 0.6rem;
      }
      .wordmark {
        font-family: 'Space Grotesk', sans-serif; font-weight: 700;
        font-size: 3.1rem; line-height: 1; margin: 0;
      }
      .wordmark .dot { color: var(--signal); }
      .tagline { color: var(--muted); font-size: 1.02rem; margin-top: 0.7rem; max-width: 46ch; }

      /* ── Stage trace ────────────────────────────────────────────── */
      .stage {
        display: flex; align-items: center; gap: 0.8rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.86rem;
        padding: 0.55rem 0; border-bottom: 1px dashed var(--line);
        color: var(--muted);
      }
      .stage .num { color: var(--signal); width: 2.4rem; }
      .stage.active { color: var(--text); }
      .stage.active .num { color: var(--signal); }
      .stage.done .num { color: var(--good); }

      /* ── Score gauge ────────────────────────────────────────────── */
      .gauge {
        background: var(--surface); border: 1px solid var(--line);
        border-radius: 14px; padding: 1.4rem 1.6rem; text-align: center;
      }
      .gauge .val {
        font-family: 'Space Grotesk', sans-serif; font-weight: 700;
        font-size: 3.4rem; line-height: 1; color: var(--cool);
      }
      .gauge .val small { font-size: 1.2rem; color: var(--muted); font-weight: 500; }
      .gauge .lbl {
        font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
        letter-spacing: 0.24em; text-transform: uppercase; color: var(--muted);
        margin-top: 0.5rem;
      }

      /* Cards / report surface */
      .panel {
        background: var(--surface); border: 1px solid var(--line);
        border-radius: 14px; padding: 1.6rem 1.8rem;
      }
      .panel-title {
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        letter-spacing: 0.24em; text-transform: uppercase; color: var(--signal);
        margin-bottom: 1rem;
      }

      /* Inputs */
      .stTextInput input, .stTextArea textarea {
        background: var(--surface2) !important; color: var(--text) !important;
        border: 1px solid var(--line) !important; border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
      }
      .stTextInput input:focus { border-color: var(--signal) !important; box-shadow: none !important; }

      /* Primary button */
      .stButton > button {
        background: var(--signal); color: #1a1205; border: none;
        border-radius: 10px; font-weight: 600; font-family: 'Space Grotesk', sans-serif;
        padding: 0.55rem 1.4rem; transition: transform .08s ease, filter .15s ease;
      }
      .stButton > button:hover { filter: brightness(1.06); transform: translateY(-1px); }
      .stButton > button:active { transform: translateY(0); }

      /* Expanders / status */
      [data-testid="stExpander"] {
        background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
      }

      /* Sidebar */
      section[data-testid="stSidebar"] { background: #0B0E12; border-right: 1px solid var(--line); }
      section[data-testid="stSidebar"] * { color: var(--text); }

      .pill {
        display: inline-flex; align-items: center; gap: 0.4rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
        padding: 0.2rem 0.6rem; border-radius: 999px; border: 1px solid var(--line);
        color: var(--muted);
      }
      .dot-ok  { width: 7px; height: 7px; border-radius: 50%; background: var(--good); }
      .dot-bad { width: 7px; height: 7px; border-radius: 50%; background: #ff6b6b; }

      a { color: var(--cool); }
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
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-family:Space Grotesk;font-weight:700;font-size:1.4rem;">'
        'Atlas<span style="color:var(--signal)">.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="color:var(--muted);font-size:0.85rem;margin-bottom:1.2rem;">'
        "Autonomous research agent</div>",
        unsafe_allow_html=True,
    )

    st.markdown("##### Pipeline")
    st.markdown(
        '<div style="font-family:JetBrains Mono;font-size:0.78rem;color:var(--muted);line-height:1.9">'
        "01 · search the web<br>02 · scrape best source<br>"
        "03 · synthesize report<br>04 · self-critique</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("##### Environment")
    for name, ok in keys_present().items():
        dot = "dot-ok" if ok else "dot-bad"
        state_txt = "loaded" if ok else "missing"
        st.markdown(
            f'<div class="pill" style="margin-bottom:6px"><span class="{dot}"></span>'
            f"{name} · {state_txt}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("Model · open-mistral-7b  ·  Search · Tavily")


# ──────────────────────────────────────────────────────────────────────────────
# Masthead
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="masthead">
      <div class="eyebrow">Multi-stage research agent</div>
      <h1 class="wordmark">Atlas<span class="dot">.</span></h1>
      <p class="tagline">Give it a topic. It searches the web, reads the best source,
      writes a structured report, then grades its own work — and shows you every step.</p>
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
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input(
        "Research topic",
        placeholder="e.g.  The economics of small modular nuclear reactors",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("Research →", use_container_width=True)

missing = [k for k, ok in keys_present().items() if not ok]

# ── Run ───────────────────────────────────────────────────────────────────────
if run:
    if not topic or not topic.strip():
        st.warning("Enter a topic to research.")
    elif missing:
        st.error(
            "Can't start — these API keys aren't loaded: "
            + ", ".join(missing)
            + ". Add them to your .env file and restart."
        )
    else:
        statuses = ["idle"] * len(STAGES)
        st.markdown('<div class="panel-title" style="margin-top:1.4rem">Agent trace</div>',
                    unsafe_allow_html=True)
        trace = st.empty()
        render_trace(trace, statuses)

        def on_stage(i, s):
            statuses[i] = s
            render_trace(trace, statuses)

        try:
            with st.spinner("Agent working…"):
                result = run_research(topic.strip(), trace, on_stage)
            st.session_state.result = result
            st.session_state.topic = topic.strip()
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
