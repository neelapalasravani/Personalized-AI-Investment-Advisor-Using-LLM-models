import logging
import re
import sqlite3
from typing import Optional

import pandas as pd
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

prompt_cache: dict = {}

INJECTION_TRIGGERS = ["delete database", "bypass", "override security", "hack"]


def extract_sql(text: str) -> Optional[str]:
    match = re.search(r"(SELECT .*?;)", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def is_prompt_injection(question: str) -> bool:
    return any(trigger in question.lower() for trigger in INJECTION_TRIGGERS)


def generate_sql(llm, question: str, schema: str) -> Optional[str]:
    if is_prompt_injection(question):
        logger.warning("Prompt injection detected in question: %r", question)
        return None

    if question in prompt_cache:
        logger.debug("Cache hit for question: %r", question)
        return prompt_cache[question]

    system_prompt = (
        "You are a highly accurate financial SQL assistant for an ETF investment database.\n"
        "Generate only valid SELECT SQL queries. Schema: " + schema + "\n"
    )
    chain_prompt = (
        f'\nUnderstand the question: "{question}".\n'
        "Convert it into a SQL SELECT query safely and reflect on correctness."
    )
    messages = [
        SystemMessage(content=system_prompt + chain_prompt),
        HumanMessage(content=question),
    ]

    try:
        logger.info("Invoking LLM for question: %r", question)
        response = llm.invoke(messages)
        sql = extract_sql(response.content)
        if sql:
            logger.info("SQL generated successfully for question: %r", question)
            prompt_cache[question] = sql
        else:
            logger.warning(
                "LLM response did not contain a valid SQL query for question: %r", question
            )
        return sql
    except Exception as e:
        logger.error(
            "LLM invocation failed for question %r: %s", question, e, exc_info=True
        )
        return None


def run_sql_query(sql_query: str, db_file: str) -> str:
    logger.info("Executing SQL query against %s: %s", db_file, sql_query)
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        result_df = pd.read_sql_query(sql_query, conn)
        conn.close()
        if result_df.empty:
            logger.info("Query returned no results.")
            return "No results found."
        logger.info("Query returned %d rows.", len(result_df))
        return result_df.head(10).to_string(index=False)
    except Exception as e:
        logger.error("SQL execution error: %s", e, exc_info=True)
        return f"SQL execution error: {e}"
