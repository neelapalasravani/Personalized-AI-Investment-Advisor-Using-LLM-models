import re
import sqlite3

import pandas as pd
from langchain.schema import HumanMessage, SystemMessage

prompt_cache = {}

def extract_sql(text):
    match = re.search(r"(SELECT .*?;)", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

def is_prompt_injection(question):
    triggers = ["delete database", "bypass", "override security", "hack"]
    return any(trigger in question.lower() for trigger in triggers)

def generate_sql(llm, question, schema):
    if is_prompt_injection(question):
        return None

    if question in prompt_cache:
        return prompt_cache[question]

    system_prompt = (
        "You are a highly accurate financial SQL assistant for an ETF investment database.\n"
        "Generate only valid SELECT SQL queries. Schema: " + schema + "\n"
    )
    chain_prompt = (
        f"\nUnderstand the question: \"{question}\".\n"
        "Convert it into a SQL SELECT query safely and reflect on correctness."
    )
    messages = [
        SystemMessage(content=system_prompt + chain_prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    sql = extract_sql(response.content)
    if sql:
        prompt_cache[question] = sql
    return sql

def run_sql_query(sql_query, db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        result_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return result_df.head(10).to_string(index=False) if not result_df.empty else "No results found."
    except Exception as e:
        return f"SQL execution error: {e}"
