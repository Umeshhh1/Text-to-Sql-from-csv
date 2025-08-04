import streamlit as st
import pandas as pd
import sqlite3
import os
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
    df = create_table_from_csv(uploaded_file)
    st.success(" Database created from uploaded CSV!")
    st.write("🧾 Preview of your data:")
    st.dataframe(df)

    schema_description = get_table_schema()

    question = st.text_input(" Ask a question about your data")

    if st.button("🔍 Get Result"):
        if question:
            try:
                sql = generate_sql(question, schema_description)
                   ## custom llm parser so used sql replace strip

                sql = sql.replace("```sql", "").replace("```", "").strip()       

                conn = sqlite3.connect(DB_PATH)
                result = conn.execute(sql).fetchall()
                cols = [desc[0] for desc in conn.execute(sql).description]

                st.write(" Query Result	:")
                df_result = pd.DataFrame(result, columns=cols)
                st.dataframe(df_result)

            except Exception as e:
                st.error(f" Error executing query: {e}")
