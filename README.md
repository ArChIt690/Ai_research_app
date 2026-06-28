<h3 align="center">Atlas · AI Research Agent</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![Built with LangChain](https://img.shields.io/badge/built%20with-LangChain%20%7C%20LangGraph-1C3C3C.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Give Atlas a topic. It searches the open web, reads the best source in depth,
writes a structured research report, then grades its own work — and shows you every step.
    <br>
</p>

## 📝 Table of Contents

- [About](#about)
- [How It Works](#how_it_works)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

**Atlas** is an autonomous, multi-stage research agent. Hand it any topic and it runs a
four-step pipeline end to end: it queries the web for reliable sources, scrapes the most
relevant page for deeper content, synthesizes everything into a structured report, and
then critiques its own report with a score out of 10.

It ships in two forms that share the exact same building blocks:

- **CLI pipeline** (`pipeline.py`) — runs the agent in the terminal, printing each stage.
- **Streamlit app** (`app.py`) — a "research console" UI where you watch each stage light
  up as it works, then get a sourced report with a critic's score and a downloadable `.md`.

Under the hood it uses **LangChain / LangGraph** ReAct agents, the **Mistral**
(`open-mistral-7b`) LLM, and the **Tavily** search API.

## 🔄 How It Works <a name = "how_it_works"></a>

The pipeline runs four stages:

| # | Stage | What it does |
|---|-------|--------------|
| 01 | **Search** | A ReAct agent uses the Tavily search tool to find reliable sources for the topic. |
| 02 | **Scrape** | A second agent picks the most relevant URL and scrapes it (BeautifulSoup) for deeper content. |
| 03 | **Synthesize** | An LCEL chain writes a structured report — Introduction, Key Findings, Conclusion, Sources. |
| 04 | **Critique** | A critic chain grades the report (`Score: X/10`) with strengths, areas to improve, and a verdict. |

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project running on your local machine for
development and testing.

### Prerequisites

- **Python 3.12** (see `.python-version`)
- API keys for **Mistral AI** and **Tavily**

### Installing

**1. Clone the repo**

```bash
git clone <your-repo-url>
cd Ai_research_app
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your API keys**

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_mistral_key_here
TAVILY_API_KEY=your_tavily_key_here
```

## 🎈 Usage <a name="usage"></a>

### Run the web app (recommended)

```bash
streamlit run app.py
```

Open the local URL Streamlit prints, enter a research topic, and hit **Research →**.
You'll watch all four stages run, then get the report, the critic's score, the raw
sources, and a button to download the report as Markdown.

### Run the CLI pipeline

```bash
python pipeline.py
```

You'll be prompted for a topic, and each stage prints to the terminal as it completes.

## ⛏️ Built Using <a name = "built_using"></a>

- [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent orchestration & LCEL chains
- [Mistral AI](https://mistral.ai/) - `open-mistral-7b` LLM
- [Tavily](https://tavily.com/) - Web search API
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
- [Streamlit](https://streamlit.io/) - Web UI
- [Pydantic](https://docs.pydantic.dev/) - Structured output validation

## ✍️ Authors <a name = "authors"></a>

- [@architchakraborty](https://github.com/architchakraborty) - Idea & Initial work

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- The LangChain / LangGraph team for the ReAct agent and LCEL primitives
- Mistral AI and Tavily for the LLM and search APIs
- README template inspired by [The Documentation Compendium](https://github.com/kylelobo/The-Documentation-Compendium)
