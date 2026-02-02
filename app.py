import streamlit as st
import pandas as pd
import sqlite3
import os
import groq
from google.api_core import exceptions
from sql import generate_sql

# ------------------ CONSTANTS ------------------
DB_PATH = "db/sample.db"
TABLE_NAME = "user_data"

# ------------------ FUNCTIONS ------------------

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
        schema_str += f"- {col[1]} ({col[2]})\n"

    return schema_str


def execute_sql(sql_query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(sql_query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    return rows, columns


def clean_sql(sql_text):
    return (
        sql_text.replace("```sql", "")
        .replace("```", "")
        .strip()
    )

# ------------------ STREAMLIT UI ------------------

st.set_page_config(page_title="Text-to-SQL from CSV", layout="wide")
st.title("📊 Text-to-SQL Generator from CSV")

uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    if "df" not in st.session_state:
        st.session_state.df = create_table_from_csv(uploaded_file)
        st.success("✅ Database created successfully!")

    st.subheader("🧾 Data Preview")
    st.dataframe(st.session_state.df, use_container_width=True)

    schema_description = get_table_schema()

    with st.expander("📐 Detected Database Schema"):
        st.code(schema_description)

    question = st.text_input("💬 Ask a question about your data")

    if st.button("🔍 Generate SQL & Run"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating SQL using Gemini..."):
                try:
                    sql_query = generate_sql(question, schema_description)
                    sql_query = clean_sql(sql_query)

                    rows, columns = execute_sql(sql_query)

                    st.subheader("📝 Generated SQL")
                    st.code(sql_query, language="sql")

                    st.subheader("📊 Query Result")
                    if rows:
                        result_df = pd.DataFrame(rows, columns=columns)
                        st.dataframe(result_df, use_container_width=True)
                    else:
                        st.info("No results found for this query.")

                except exceptions.ResourceExhausted:
                    st.error(
                        "🚨 **Quota Exceeded (429)**\n\n"
                        "Please wait a minute or switch to another model "
                        "(e.g., `gemini-1.5-pro`) in `sql.py`."
                    )
                except sqlite3.Error as db_err:
                    st.error(f"❌ SQL Execution Error:\n{db_err}")
                except Exception as e:
                    st.error(f"❌ Unexpected Error:\n{e}")
