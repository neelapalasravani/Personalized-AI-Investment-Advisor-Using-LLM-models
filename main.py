import os
import sys
import yaml
import logging
import pandas as pd
import sqlite3

from src.ui import build_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === Load API Keys ===
try:
    with open("config/api_keys.yaml") as f:
        api_keys = yaml.safe_load(f)
    logger.info("API keys loaded successfully.")
except FileNotFoundError:
    logger.error("Config file 'config/api_keys.yaml' not found.")
    sys.exit(1)
except yaml.YAMLError as e:
    logger.error(f"Failed to parse API keys config: {e}")
    sys.exit(1)

# === Load ETF dataset into SQLite ===
data_path = "data/etf_dataset_sample.csv"
db_file = "etf_database.db"

try:
    df = pd.read_csv(data_path)
    conn = sqlite3.connect(db_file)
    df.to_sql("etf_prices", conn, if_exists="replace", index=False)
    conn.close()
    logger.info("ETF dataset loaded into SQLite successfully.")
except FileNotFoundError:
    logger.error(f"Dataset file '{data_path}' not found.")
    sys.exit(1)
except Exception as e:
    logger.error(f"Failed to load ETF dataset into SQLite: {e}")
    sys.exit(1)

# === Extract schema for prompting ===
try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(etf_prices)")
    columns = cursor.fetchall()
    schema = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
    conn.close()
    logger.info("Database schema extracted successfully.")
except Exception as e:
    logger.error(f"Failed to extract database schema: {e}")
    sys.exit(1)

# === Launch Gradio App ===
try:
    demo = build_app(schema, db_file, api_keys)
    demo.launch()
except Exception as e:
    logger.error(f"Failed to launch the application: {e}")
    sys.exit(1)
