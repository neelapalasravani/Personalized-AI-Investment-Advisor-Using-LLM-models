import logging

import gradio as gr

from Src.llm_interface import get_llm_instances
from Src.web_search import tavily_search
from Src.Main_pipeline import generate_sql, run_sql_query, is_prompt_injection
from Src.utils import format_web_summary

logger = logging.getLogger(__name__)


def build_app(schema: str, db_file: str, api_keys: dict):
    try:
        llm_instances = get_llm_instances(api_keys.get("together"))
    except Exception as e:
        logger.error("Failed to initialize LLM instances: %s", e, exc_info=True)
        raise

    def sql_qa_pipeline(question: str, model_name: str) -> str:
        llm = llm_instances.get(model_name)
        if llm is None:
            logger.error("Unknown model requested: %r", model_name)
            return f"Error: unknown model '{model_name}'."
        sql = generate_sql(llm, question, schema)
        if sql:
            return (
                f"**Query:**\n```sql\n{sql}\n```\n\n**Results:**\n"
                + run_sql_query(sql, db_file)
            )
        logger.info(
            "No SQL generated; falling back to web search for question: %r", question
        )
        return format_web_summary(question, tavily_search(question, api_keys.get("tavily")))

    def handle_query(dropdown: str, custom: str, model_name: str) -> str:
        query = custom.strip() if custom.strip() else dropdown
        if not query or query == "--Select--":
            return "Please select a valid question or type one."
        if is_prompt_injection(query):
            logger.warning("Injection attempt blocked for query: %r", query)
            return "Security alert: Unsafe input detected."
        try:
            return sql_qa_pipeline(query, model_name)
        except Exception as e:
            logger.error(
                "Unhandled error in handle_query for %r: %s", query, e, exc_info=True
            )
            return "An unexpected error occurred. Please try again."

    with gr.Blocks() as demo:
        gr.Markdown("## Long-term Investment Advisor")
        model_choice = gr.Radio(
            ["Llama-3.3-70B", "Mistral-7B"], label="LLM", value="Llama-3.3-70B"
        )
        dropdown_query = gr.Dropdown(
            choices=["--Select--", "Top 5 ETFs by price", "Latest news about ETF market"],
            label="Select a Question",
        )
        custom_query = gr.Textbox(label="Or type your question")
        submit = gr.Button("Submit")
        output = gr.Textbox(lines=20, label="Assistant Response")
        submit.click(
            fn=handle_query,
            inputs=[dropdown_query, custom_query, model_choice],
            outputs=output,
        )
    return demo
