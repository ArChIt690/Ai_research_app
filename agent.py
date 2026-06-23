from tools import web_search_tool, scrape_tool
from dotenv import load_dotenv
import os
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatMistralAI(
    model_name = "open-mistral-7b",
    temperature = 0,
    api_key = os.getenv("MISTRAL_API_KEY"),
)

#1st agent for web search
def search_web_agent():
    return create_agent(
        model = llm,
        tools = [web_search_tool],
    )

#2nd agent for scraping
def scrape_web_agent():
    return create_agent(
        model = llm,
        tools = [scrape_tool],
    )

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

    Topic: {topic}

    Research Gathered:
    {research}

    Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)

    Be detailed, factual and professional."""),
    ])


summary_chain = summary_prompt | llm | StrOutputParser()

report_critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

    Report:
    {report}

    Respond in this exact format:

    Score: X/10

    Strengths:
    - ...
    - ...

    Areas to Improve:
    - ...
    - ...

    One line verdict:
    ..."""),
    ])

critic_chain = report_critic_prompt | llm | StrOutputParser()

