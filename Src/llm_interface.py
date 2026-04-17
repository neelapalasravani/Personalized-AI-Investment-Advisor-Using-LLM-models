import logging
from langchain_together import ChatTogether
from langchain.schema import HumanMessage, SystemMessage  # noqa: F401 — re-exported for pipeline use

logger = logging.getLogger(__name__)

MODEL_MAP = {
    "Llama-3.3-70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "Mistral-7B": "mistralai/Mistral-7B-Instruct-v0.3",
}


def get_llm_instances(api_key: str) -> dict:
    if not api_key or not api_key.strip():
        raise ValueError("Together API key is missing or empty")

    instances = {}
    for name, model_id in MODEL_MAP.items():
        try:
            instances[name] = ChatTogether(
                together_api_key=api_key,
                model=model_id,
            )
            logger.info("Initialised LLM instance: %s (%s)", name, model_id)
        except Exception as exc:
            logger.error("Failed to initialise LLM %s: %s", name, exc, exc_info=True)
            raise
    return instances
