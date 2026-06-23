from agent import search_web_agent, scrape_web_agent, summary_chain, critic_chain

def research_pipeline(topic: str) -> dict:
    state={}

    print("="*50)
    print("\n STEP 1: Searching the web for relevant information...\n")
    print("="*50)

    #search url agent
    search_agent = search_web_agent()
    search_results = search_agent.invoke(
        {
            "messages" : [("user", f"Find reliable and relevant information about the topic {topic}")]
        }
    )
    state['search_results'] = search_results['messages'][-1].content

    #scrap the datas from the urls
    print("="*50)
    print("\n STEP 2: Scraping the content from the relevant urls...\n")
    print("="*50)

    reader_agent = scrape_web_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state['reader_result'] = reader_result['messages'][-1].content

    print (f"scraped content : {state['reader_result']}")

    #summary chain
    print("="*50)
    print("\n STEP 3: Creating a summary of the research...\n")
    print("="*50)

    summary_agent = summary_chain
    research_total =( 
                        f"Search results : {state['search_results']}"
                        f" Scraped content : {state['reader_result']}"
                    )
    
    state['summary_result'] = summary_agent.invoke({
        "topic" : topic,
        "research" : research_total,
    })

    print (f"final report : {state['summary_result']}")

    #critic chain
    print("="*50)
    print("\n STEP 4: Reviewing the research report...\n")
    print("="*50)

    state['critic_result'] = critic_chain.invoke({
        "report" : state['summary_result'],
    })

    print (f"final critic : {state['critic_result']}")
     
    return state

if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    research_pipeline(topic)