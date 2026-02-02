from groq import Groq
import streamlit as st

# Create Groq client using secret
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_sql(question, schema_description):
    prompt = f"""
You are a smart assistant that understands casual daily English
and converts it into SQLite SQL queries.

Your task:
1. Understand informal / vague / daily English
2. Infer missing details using common sense
3. Convert it into a valid SQLite SQL query

STRICT RULES:
- Output ONLY SQL
- No explanation
- No markdown
- No English text
- Start directly with SELECT

Database schema:
{schema_description}

User question (casual English):
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()
