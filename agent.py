from tools import web_search_tool, scrape_tool
from dotenv import load_dotenv
import os
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatMistralAI(
    model_name = "mistralai/Mistral-7B-Instruct-v0.1",
    temperature = 0,
    api_key = os.getenv("MISTRAL_API_KEY"),
)

#1st agent for web search
def search_web_agent():
    return create_agent(
        llm = llm,
        tools = [web_search_tool],
    )

#2nd agent for scraping
def scrape_web_agent():
    return create_agent(
        llm = llm,
        tools = [scrape_tool],
    )

summary_prompt = ChatPromptTemplate.from_messages([
    (" system" ,
            "You are an expert research report writer. Your job is to turn raw research, "
            "a draft summary, and a reviewer's critique into a single polished, well-structured "
            "report that fully answers the user's query.\n\n"
            "Rules:\n"
            "- Use ONLY information supported by the research content; never invent facts or sources.\n"
            "- Treat the critique as a checklist: fix every weakness it raises, fill the gaps it "
            "names, and remove or qualify any unsupported claim it flags.\n"
            "- The draft summary is a starting point, not a constraint — expand, correct, and "
            "restructure it as needed.\n"
            "- Be objective and precise. Where sources disagree, say so instead of picking one.\n"
            "- Cite the relevant source URLs inline so every claim is traceable.\n\n"
            "Format the report in clean Markdown:\n"
            "- A short, specific title (H1)\n"
            "- A 2-3 sentence executive summary\n"
            "- Logically ordered sections with H2 headings\n"
            "- A brief conclusion\n"
            "- A 'Sources' list of the URLs you used",), 
    ("human",
            "User query:\n{query}\n\n"
            "Research content:\n{content}\n\n"
            "Draft summary:\n{summary}\n\n"
            "Reviewer critique:\n{critique}\n\n"
            "Write the final report.",)
    ])

summary_chain = summary_prompt | llm | StrOutputParser()

report_critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a rigorous report reviewer. You are given the user's query, the source "
            "research content, and a finished report. Evaluate the report strictly against the "
            "query and the sources.\n\n"
            "Score the report from 1 to 10 on each of these, then give an overall score:\n"
            "- Accuracy: every claim supported by the research content; nothing invented or "
            "contradicted.\n"
            "- Completeness: fully answers the query, no missing angle a reader would expect.\n"
            "- Citations: source URLs present and attached to the right claims.\n"
            "- Structure & clarity: well-organised, no padding, repetition, or vagueness.\n"
            "- Objectivity: no bias or unjustified certainty; conflicting sources noted.\n\n"
            "Then list the areas to improve: concrete, actionable fixes the writer should make, "
            "ordered most important first. Each item must point to the exact section or claim "
            "and say what to change and why. If a criterion scored 8 or above, don't pad the "
            "list with notes about it. If the report is already strong, say so and keep the "
            "list short or empty.\n\n"
            "End your response with these lines in EXACTLY this format and nothing after the "
            "VERDICT line:\n"
            "AREAS TO IMPROVE:\n"
            "1. <most important fix>\n"
            "2. <next fix>\n"
            "3. <next fix>   (add or remove numbered items as needed)\n"
            "SCORES: accuracy=<n>, completeness=<n>, citations=<n>, structure=<n>, objectivity=<n>\n"
            "OVERALL: <n>/10\n"
            "VERDICT: APPROVED   (only if OVERALL >= 8 and no single score is below 6)\n"
            "VERDICT: REVISE     (otherwise)",
        ),
        (
            "human",
            "User query:\n{query}\n\n"
            "Source content:\n{content}\n\n"
            "Report to review:\n{report}\n\n"
            "Review the report.",
        ),
    ]
)

critic_chain = report_critic_prompt | llm | StrOutputParser()

