import google.generativeai as genai

genai.configure(api_key="AIzaSyA0qj7AoWiAuG03rhrgTAG0uuqt9mjoBK8")

model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def generate_sql(prompt, schema_description):
    full_prompt = f"""
You are an AI assistant that converts natural language into SQL queries.
Here is the database schema:

{schema_description}

Convert the following question into a valid SQL query:
\"{prompt}\"
"""
    response = model.generate_content(full_prompt)
    return response.text.strip()
