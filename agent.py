import os
from langchain_community.document_loaders import ArxivLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import resend
from dotenv import load_dotenv

# Load variables from .env file for local testing
load_dotenv()

def run_research_agent():
    # 1. Setup Data Loader (Limited to 10k chars to prevent memory crashes)
    loader = ArxivLoader(query="Artificial Intelligence", load_max_docs=3, doc_content_chars_max=10000)
    docs = loader.load()
    
    # 2. Setup Gemini Model
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # 3. Define the Prompt with HTML instructions
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
    
    # 4. Generate the Digest
    newsletter_content = chain.invoke({"context": docs})
    
    # 5. Email via Resend
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    # Wrap in a styled container for a professional look
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: auto;">
        {newsletter_content}
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <footer style="font-size: 0.8em; color: #777;">
            Sent by your Autonomous AI Agent | <a href="https://github.com/Fervid-S">View on GitHub</a>
        </footer>
    </div>
    """

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "sidhant.singh.ml@gmail.com", # REPLACE WITH YOUR EMAIL
        "subject": "🚀 Daily Groundbreaking AI Update",
        "html": html_body
    })
    print("Email sent successfully!")

if __name__ == "__main__":
    run_research_agent()