import streamlit as st
import pandas as pd
import sqlite3
import os
import time
from google.api_core import exceptions
from sql import generate_sql 

DB_PATH = "db/sample.db"
TABLE_NAME = "user_data"

def create_table_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.close()
    return df

def get_table_schema():
    if not os.path.exists(DB_PATH):
        return "No database found."
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({TABLE_NAME});")
    schema_info = cursor.fetchall()
    conn.close()

    schema_str = f"Table: {TABLE_NAME}\nColumns:\n"
    for col in schema_info:
        schema_str += f"- {col[1]}: {col[2]}\n"
    return schema_str

# --------------------- Streamlit -----------------------

st.set_page_config(page_title="Text-to-SQL", layout="wide")
st.title("📊 Text-to-SQL Generator from CSV")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    # Use session state to avoid re-processing CSV on every interaction
    if "df" not in st.session_state:
        st.session_state.df = create_table_from_csv(uploaded_file)
        st.success("✅ Database created from uploaded CSV!")

    st.write("🧾 Preview of your data:")
    st.dataframe(st.session_state.df)

    schema_description = get_table_schema()
    question = st.text_input("💬 Ask a question about your data")

    if st.button("🔍 Get Result"):
        if question:
            with st.spinner("Generating SQL..."):
                try:
                    # Attempt to generate SQL
                    sql = generate_sql(question, schema_description)
                    
                    # Clean the SQL string
                    sql = sql.replace("```sql", "").replace("```", "").replace("sql", "").strip()       

                    # Execute in SQLite
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.execute(sql)
                    result = cursor.fetchall()
                    cols = [desc[0] for desc in cursor.description]
                    conn.close()

                    st.write("### 📝 SQL Query Generated:")
                    st.code(sql, language="sql")

                    st.write("### 📊 Query Result:")
                    if result:
                        df_result = pd.DataFrame(result, columns=cols)
                        st.dataframe(df_result)
                    else:
                        st.warning("No data found for this query.")

                except exceptions.ResourceExhausted:
                    st.error("🚨 **Quota Exceeded (429):** You've sent too many requests. Please wait 60 seconds or switch to a different model in your `sql.py` file.")
                except Exception as e:
                    st.error(f"❌ Error executing query: {e}")
