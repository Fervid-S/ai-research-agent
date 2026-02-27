import os
from langchain_community.document_loaders import ArxivLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import resend
from dotenv import load_dotenv

load_dotenv()

def run_research_agent():
    # ... (Keep your loader and model setup the same)

    # 1. UPDATED PROMPT: Ask for HTML formatting
    template = """
    You are a top-tier AI researcher writing a daily newsletter.
    Summarize the following papers using clean HTML formatting.
    
    Use <h2> for the main title, <h3> for paper titles, <b> for emphasis, 
    and <br><br> for clear spacing between paragraphs.
    Ensure there is a horizontal line <hr> between each paper summary.

    Papers: {context}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    # 2. Generate the Digest
    newsletter_content = chain.invoke({"context": docs})
    
    # 3. Email via Resend (Wrap it in a container for better looks)
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    # We wrap the content in a <div> with a specific font for professional looks
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: auto;">
        {newsletter_content}
        <footer style="margin-top: 20px; font-size: 0.8em; color: #777;">
            Sent by your Autonomous AI Agent | <a href="https://github.com/YOUR_USERNAME">View on GitHub</a>
        </footer>
    </div>
    """

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "your-email@example.com",
        "subject": "🚀 Daily Groundbreaking AI Update",
        "html": html_body  # Now using our styled html_body
    })

if __name__ == "__main__":
    run_research_agent()