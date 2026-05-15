import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.llm_interface import get_llm_instances


@dataclass(frozen=True)
class AppSettings:
    """Filesystem + runtime configuration loaded from environment variables.

    Defaults mirror the paths used by the legacy Gradio entrypoint (``main.py``)
    so that the FastAPI layer is a drop-in alternative without requiring a
    config change.
    """

    api_keys_path: Path
    data_csv_path: Path
    db_file: Path

    @classmethod
    def load(cls) -> "AppSettings":
        return cls(
            api_keys_path=Path(
                os.getenv("ROBRAIN_API_KEYS_PATH", "config/api_keys.yaml")
            ),
            data_csv_path=Path(
                os.getenv("ROBRAIN_DATA_PATH", "data/etf_dataset_sample.csv")
            ),
            db_file=Path(os.getenv("ROBRAIN_DB_FILE", "etf_database.db")),
        )


@dataclass
class AppState:
    """Resources resolved once at startup and reused across requests."""

    schema: str
    db_file: str
    api_keys: dict[str, Any]
    llm_instances: dict[str, Any]


def build_app_state(settings: AppSettings) -> AppState:
    with open(settings.api_keys_path) as f:
        api_keys = yaml.safe_load(f)

    df = pd.read_csv(settings.data_csv_path)
    conn = sqlite3.connect(str(settings.db_file))
    try:
        df.to_sql("etf_prices", conn, if_exists="replace", index=False)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(etf_prices)")
        columns = cursor.fetchall()
    finally:
        conn.close()

    schema = ", ".join(f"{col[1]} ({col[2]})" for col in columns)

    return AppState(
        schema=schema,
        db_file=str(settings.db_file),
        api_keys=api_keys,
        llm_instances=get_llm_instances(api_keys["together"]),
    )
