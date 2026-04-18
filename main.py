import logging
import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv

from Src.ui import build_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_data_to_sqlite(data_path: str, db_file: str, table_name: str = "etf_prices") -> None:
    logger.info("Loading ETF dataset from %s into SQLite at %s", data_path, db_file)
    df = pd.read_csv(data_path)
    conn = sqlite3.connect(db_file)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        logger.info("Loaded %d rows into table '%s'", len(df), table_name)
    finally:
        conn.close()


def extract_schema(db_file: str, table_name: str = "etf_prices") -> str:
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        logger.info("Extracted schema: %s", schema)
        return schema
    finally:
        conn.close()


def main() -> None:
    load_dotenv()

    data_path = os.getenv("ETF_DATA_PATH", "Data/etf_dataset_sample.csv")
    db_file = os.getenv("ETF_DB_FILE", "etf_database.db")
    together_api_key = os.getenv("TOGETHER_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    server_port = int(os.getenv("SERVER_PORT", "7860"))
    server_name = os.getenv("SERVER_NAME", "0.0.0.0")

    if not together_api_key:
        raise EnvironmentError("TOGETHER_API_KEY is not set in environment.")
    if not tavily_api_key:
        raise EnvironmentError("TAVILY_API_KEY is not set in environment.")

    api_keys = {"together": together_api_key, "tavily": tavily_api_key}

    load_data_to_sqlite(data_path, db_file)
    schema = extract_schema(db_file)

    logger.info("Launching Gradio app on %s:%d", server_name, server_port)
    demo = build_app(schema, db_file, api_keys)
    demo.launch(server_name=server_name, server_port=server_port)


if __name__ == "__main__":
    main()
