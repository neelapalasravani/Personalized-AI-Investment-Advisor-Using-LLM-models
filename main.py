import os
import logging
import yaml
import pandas as pd
import sqlite3

from src.ui import build_app

# === Configure logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Load API Keys ===
logger.info("Loading API keys from config/api_keys.yaml")
with open("config/api_keys.yaml") as f:
    api_keys = yaml.safe_load(f)

# === Load ETF dataset into SQLite ===
data_path = "data/etf_dataset_sample.csv"
db_file = "etf_database.db"
logger.info("Loading ETF dataset from %s", data_path)
df = pd.read_csv(data_path)
conn = sqlite3.connect(db_file)
df.to_sql("etf_prices", conn, if_exists="replace", index=False)
conn.close()
logger.info("ETF dataset loaded into SQLite database: %s", db_file)

# === Extract schema for prompting ===
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(etf_prices)")
columns = cursor.fetchall()
schema = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
conn.close()
logger.info("Extracted ETF prices schema: %s", schema)

# === Launch Gradio App ===
logger.info("Launching Gradio app")
demo = build_app(schema, db_file, api_keys)
demo.launch()
