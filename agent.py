import os
import requests
from langchain_community.document_loaders import ArxivLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import resend
from dotenv import load_dotenv

# Load variables from .env file for local testing
load_dotenv()

def fetch_ai_news():
    """Fetches the top 5 AI news headlines from NewsData.io."""
    api_key = os.getenv("NEWSDATA_API_KEY")
    # Query for 'artificial intelligence' in English
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q=artificial%20intelligence&language=en"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        news_items = []
        if "results" in data:
            for article in data["results"][:5]: # Limit to top 5 articles
                title = article.get("title", "No Title")
                desc = article.get("description", "No description available.")
                link = article.get("link", "#")
                news_items.append(f"Source: Tech News\nTitle: {title}\nSummary: {desc}\nLink: {link}")
        
        return "\n\n".join(news_items) if news_items else "No tech news found today."
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Could not retrieve tech news at this time."

def run_research_agent():
    # 1. Fetch Research Papers (Limited to 10k chars for GitHub Runner safety)
    print("Fetching arXiv papers...")
    loader = ArxivLoader(
        query="Artificial Intelligence", 
        load_max_docs=3,
        doc_content_chars_max=10000 
    )
    docs = loader.load()
    
    # 2. Fetch Latest Industry News
    print("Fetching latest AI news...")
    tech_news = fetch_ai_news()
    
    # 3. Setup Gemini Model (Using stable 2026 alias)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # 4. Define the Integrated Prompt
    template = """
    You are an expert AI Research Analyst. Create a high-quality daily newsletter using the context provided.
    
    Structure the email into two clear sections:
    1. 'Deep Dive Research' - Summarize the academic papers from arXiv.
    2. 'AI Industry Headlines' - Briefly summarize the latest tech news stories.

    Formatting Rules:
    - Use <h2> for section titles.
    - Use <h3> for individual paper/article titles.
    - Use <b> for key terms.
    - Use <br><br> for paragraph spacing.
    - Include a clickable <a href="...">Link</a> for every item.
    - Use <hr> to separate the two main sections.

    Context:
    {context}
    """
    
    combined_context = f"--- RESEARCH PAPERS ---\n{docs}\n\n--- TECH NEWS ---\n{tech_news}"
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    # 5. Generate the Final Newsletter
    print("Generating newsletter content...")
    newsletter_content = chain.invoke({"context": combined_context})
    
    # 6. Dispatch via Resend
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    html_body = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #2c3e50; max-width: 650px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 8px;">
        <h1 style="color: #2980b9; text-align: center;">🚀 12-Hour AI Intelligence Update</h1>
        <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">Your automated briefing on Research & Industry Trends</p>
        <hr style="border: 0; border-top: 2px solid #3498db; margin: 20px 0;">
        
        {newsletter_content}
        
        <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 0.8em; color: #95a5a6; text-align: center;">
            <p>Sent by your Autonomous LangChain Agent</p>
            <p><a href="https://github.com/Fervid-S/ai-research-agent" style="color: #3498db; text-decoration: none;">View Source on GitHub</a></p>
        </div>
    </div>
    """

    print("Sending email...")
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "sidhant.singh.ml@gmail.com", # REPLACE THIS
        "subject": "🤖 Your 12-Hour AI Digest",
        "html": html_body
    })
    print("Success! Check your inbox.")

if __name__ == "__main__":
    run_research_agent()