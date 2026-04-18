import logging
import os
from typing import Optional

from langchain_together import ChatTogether
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


def get_llm_instances(api_key: Optional[str] = None) -> dict:
    key = api_key or os.getenv("TOGETHER_API_KEY")
    if not key:
        raise EnvironmentError("TOGETHER_API_KEY is not set.")
    logger.info("Initializing LLM instances.")
    return {
        "Llama-3.3-70B": ChatTogether(
            together_api_key=key,
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        ),
        "Mistral-7B": ChatTogether(
            together_api_key=key,
            model="mistralai/Mistral-7B-Instruct-v0.3",
        ),
    }
