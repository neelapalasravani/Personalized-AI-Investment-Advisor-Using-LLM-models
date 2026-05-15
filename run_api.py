"""Entrypoint for the FastAPI server.

Usage:
    python run_api.py
    # or, for hot-reload during development:
    uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

Environment overrides (all optional):
    ROBRAIN_API_KEYS_PATH   path to api_keys.yaml   (default: config/api_keys.yaml)
    ROBRAIN_DATA_PATH       path to ETF CSV         (default: data/etf_dataset_sample.csv)
    ROBRAIN_DB_FILE         sqlite DB filename      (default: etf_database.db)
"""

import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "src.api.app:app",
        host=os.getenv("ROBRAIN_API_HOST", "0.0.0.0"),
        port=int(os.getenv("ROBRAIN_API_PORT", "8000")),
        reload=os.getenv("ROBRAIN_API_RELOAD", "false").lower() == "true",
    )
