import os
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))

@tool
def web_search_tool(query : str) ->str:
    """ do a web search and give me reliable and relevant information about the query from the web and return mye the title , content snippets and the website links"""