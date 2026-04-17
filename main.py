import os
import sys
import logging
import sqlite3
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging — configure before any application imports so all modules inherit
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger(__name__)

# Load .env in development (no-op if python-dotenv not installed or file absent)
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env")
except ImportError:
    logger.debug("python-dotenv not installed — skipping .env loading")

import pandas as pd
from Src.ui import build_app


def load_api_keys() -> dict:
    together_key = os.environ.get("TOGETHER_API_KEY", "").strip()
    tavily_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not together_key:
        raise ValueError("TOGETHER_API_KEY environment variable is not set or empty")
    if not tavily_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set or empty")
    return {"together": together_key, "tavily": tavily_key}


def load_etf_data(data_path: str, db_file: str) -> None:
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"ETF dataset not found: {path.resolve()}")

    logger.info("Loading ETF data from %s", path)
    df = pd.read_csv(path)
    logger.info("Read %d rows from CSV", len(df))

    conn = sqlite3.connect(db_file)
    try:
        df.to_sql("etf_prices", conn, if_exists="replace", index=False)
        logger.info("ETF data written to SQLite database: %s", db_file)
    finally:
        conn.close()


def get_schema(db_file: str) -> str:
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(etf_prices)")
        columns = cursor.fetchall()
        schema = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        logger.info("Extracted table schema: %s", schema)
        return schema
    finally:
        conn.close()


def main() -> None:
    data_path = os.environ.get("ETF_DATA_PATH", "data/etf_dataset_sample.csv")
    db_file = os.environ.get("ETF_DB_FILE", "etf_database.db")

    logger.info("Starting Personalized AI Investment Advisor")

    try:
        api_keys = load_api_keys()
    except ValueError as exc:
        logger.critical("Configuration error: %s", exc)
        sys.exit(1)

    try:
        load_etf_data(data_path, db_file)
        schema = get_schema(db_file)
    except FileNotFoundError as exc:
        logger.critical("Data file error: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.critical("Failed to initialise ETF database: %s", exc, exc_info=True)
        sys.exit(1)

    try:
        demo = build_app(schema, db_file, api_keys)
        host = os.environ.get("APP_HOST", "0.0.0.0")
        port = int(os.environ.get("APP_PORT", "7860"))
        share = os.environ.get("APP_SHARE", "false").lower() == "true"
        logger.info("Launching Gradio app on %s:%s (share=%s)", host, port, share)
        demo.launch(server_name=host, server_port=port, share=share)
    except Exception as exc:
        logger.critical("Failed to launch application: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
