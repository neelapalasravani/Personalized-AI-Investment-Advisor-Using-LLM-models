import re
import logging
import sqlite3
import pandas as pd
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

prompt_cache: dict = {}


def extract_sql(text: str) -> str | None:
    match = re.search(r"(SELECT .*?;)", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def is_prompt_injection(question: str) -> bool:
    triggers = ["delete database", "bypass", "override security", "hack"]
    return any(trigger in question.lower() for trigger in triggers)


def generate_sql(llm, question: str, schema: str) -> str | None:
    if is_prompt_injection(question):
        logger.warning("Prompt injection attempt detected: %r", question)
        return None

    if question in prompt_cache:
        logger.debug("Cache hit for question: %r", question)
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
        HumanMessage(content=question),
    ]

    try:
        response = llm.invoke(messages)
        sql = extract_sql(response.content)
        if sql:
            prompt_cache[question] = sql
            logger.info("Generated SQL for question %r: %s", question, sql)
        else:
            logger.warning("LLM response contained no valid SQL for question: %r", question)
        return sql
    except Exception as exc:
        logger.error("LLM invocation failed for question %r: %s", question, exc, exc_info=True)
        return None


def run_sql_query(sql_query: str, db_file: str) -> str:
    logger.debug("Executing SQL: %s", sql_query)
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        try:
            result_df = pd.read_sql_query(sql_query, conn)
        finally:
            conn.close()
        if result_df.empty:
            logger.info("SQL query returned no results")
            return "No results found."
        logger.info("SQL query returned %d rows", len(result_df))
        return result_df.head(10).to_string(index=False)
    except Exception as exc:
        logger.error("SQL execution error: %s", exc, exc_info=True)
        return f"SQL execution error: {exc}"
