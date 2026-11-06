
import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Connect to Gemini
client = genai.Client(api_key=API_KEY) if API_KEY else None


def generate_customer_response(subject, description, category, priority):
    """
    Generate a suggested customer support response using Gemini.
    """

    if client is None:
        return "AI service is not configured. Please check the API key."

    prompt = f"""
    You are a professional and friendly customer support assistant.

    A customer has submitted this support ticket:

    Subject: {subject}
    Description: {description}
    Category: {category}
    Priority: {priority}

    Write a polite, clear and helpful response to the customer.

    Do not claim that an issue has been fixed.
    Do not invent refunds, timelines or actions.
    If more information is needed, politely ask the customer.
    Keep the response between 50 and 100 words.
    """

    try:
        result = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return result.text

    except Exception as error:
        print("Gemini API error:", error)
        return "Unable to generate an AI suggestion right now. Please try again."
