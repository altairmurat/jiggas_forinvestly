import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=OPENAI_API_KEY)

#function to ask GPT for analysis
def ask_gpt(chat_text: str, instruction: str) -> str:
    prompt = f"""You are an unbiased conversation analyst.
Conversation:
{chat_text}

Task:
{instruction}

Respond clearly, VERYVERY VERY shortly and directly to my task with examples from the chat history only AND not use curse words from the chat AND PLEASE write it more readable with paragraphs and font. 
"""
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.7)
    return response.choices[0].message.content
