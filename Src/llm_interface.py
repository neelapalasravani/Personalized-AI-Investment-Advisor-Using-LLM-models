import logging
from langchain_together import ChatTogether
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

def get_llm_instances(api_key):
    llm_configs = {
        "Llama-3.3-70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "Mistral-7B": "mistralai/Mistral-7B-Instruct-v0.3"
    }
    instances = {}
    for name, model in llm_configs.items():
        try:
            instances[name] = ChatTogether(
                together_api_key=api_key,
                model=model
            )
            logger.info(f"LLM instance '{name}' initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM '{name}': {e}")
    return instances
