import os
import arxiv
from newsdataapi import NewsDataApiClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from resend import Emails
from dotenv import load_dotenv

load_dotenv()

# 1. Fetch LATEST arXiv Papers (Sorted by Date)
def get_latest_arxiv():
    client = arxiv.Client()
    # Sort by SubmittedDate in Descending order to get new papers every 12h
    search = arxiv.Search(
        query="cat:cs.AI OR cat:cs.LG", 
        max_results=3,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    results = client.results(search)
    return [{"title": r.title, "summary": r.summary, "url": r.entry_id} for r in results]

# 2. Fetch NewsData.io (With broader query fallback)
def get_ai_news():
    try:
        api = NewsDataApiClient(apikey=os.getenv("NEWSDATA_API_KEY"))
        # Using a broader query 'artificial intelligence' increases hit rate
        response = api.news_api(q="artificial intelligence", language="en", category="technology")
        
        if response['status'] == 'success' and response['totalResults'] > 0:
            return [{"title": n['title'], "desc": n['description'], "link": n['link']} for n in response['results'][:3]]
        return []
    except Exception as e:
        print(f"News API Error: {e}")
        return []

# 3. LangChain Synthesis Logic
def summarize_updates(papers, news):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    template = """You are a world-class AI researcher. Summarize the following updates into a professional briefing.
    Research Papers: {papers}
    News Items: {news}
    Format the output in clean Markdown with bold headers."""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    return chain.invoke({"papers": papers, "news": news}).content

# 4. Main Execution
if __name__ == "__main__":
    papers = get_latest_arxiv()
    news = get_ai_news()
    
    briefing = summarize_updates(papers, news)
    
    # Send via Resend
    os.environ["RESEND_API_KEY"] = os.getenv("RESEND_API_KEY")
    Emails.send({
        "from": "onboarding@resend.dev",
        "to": "sidhant.singh.ml@gmail.com",
        "subject": "Daily AI Research Briefing",
        "html": f"<pre>{briefing}</pre>"
    })
    print("Agent execution complete.")