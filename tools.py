import os
from dotenv import load_dotenv
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from rich import print

load_dotenv()

tavily_client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))

@tool
def web_search_tool(query : str) ->str:
    """ do a web search and give me reliable and relevant information about the query from the web and return mye the title , content snippets and the website links"""
    web_search_results = tavily_client.search(query = query , max_results = 5)
    out=[]
    for r in web_search_results['results']:
        out.append(f"title : {r['title']} \n content : {r['content'][:300]} \n url : {r['url']}\n ")
    return "\n--------\n".join(out)


@tool
def scrape_tool(url : str) -> str:
    """scrape and give content of the given url for deeper reading """
    try:
        resp= requests.get(url , timeout=10 , headers={'User-Agent': 'Mozilla/5.0'})
        soup= BeautifulSoup(resp.content, 'html.parser')
        for r in soup(["script", "style" , "nav" , "footer"]):
            r.decompose()
        return soup.get_text(separator = " ", strip = True)[:3000]
    except Exception as e:
        print(f"Error occurred while scraping {url}: {str(e)}")
        return "Error occurred while scraping the URL."
print(scrape_tool.invoke("https://www.hindustantimes.com/india-news/lucknow-fire-news-live-updates-aliganj-death-toll-police-firefighters-injured-cm-yogi-adityanath-up-101782129134023.html"))

