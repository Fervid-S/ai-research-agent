import os
from langchain_community.document_loaders import ArxivLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import resend
from dotenv import load_dotenv

load_dotenv()

def run_research_agent():
    # 1. Fetch Latest AI Papers (Max 3)
    loader = ArxivLoader(query="Artificial Intelligence", load_max_docs=3)
    docs = loader.load()
    
    # 2. Setup Gemini 3 Flash (Free Tier)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    
    # 3. Summarization Chain
    template = "You are a top-tier AI researcher. Summarize these groundbreaking papers for a daily newsletter: {context}"
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    # 4. Generate the Content to be delivered
    newsletter_content = chain.invoke({"context": docs})
    
    # 5. Send to Email via Resend
    resend.api_key = os.getenv("RESEND_API_KEY")
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "sidhant.singh.ml@gmail.com",
        "subject": "🚀 Daily Groundbreaking AI Update",
        "html": f"<h2>Today's AI Research Highlights</h2><p>{newsletter_content}</p>"
    })

if __name__ == "__main__":
    run_research_agent()