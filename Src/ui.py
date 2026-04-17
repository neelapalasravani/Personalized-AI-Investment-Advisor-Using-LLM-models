import logging
import gradio as gr
from Src.llm_interface import get_llm_instances
from Src.web_search import tavily_search
from Src.Main_pipeline import generate_sql, run_sql_query, is_prompt_injection
from Src.utils import format_web_summary

logger = logging.getLogger(__name__)

PREDEFINED_QUESTIONS = [
    "--Select--",
    "Top 5 ETFs by price",
    "Latest news about ETF market",
]


def build_app(schema: str, db_file: str, api_keys: dict):
    try:
        llm_instances = get_llm_instances(api_keys["together"])
    except Exception as exc:
        logger.critical("Cannot build app — LLM initialisation failed: %s", exc)
        raise

    def sql_qa_pipeline(question: str, model_name: str) -> str:
        llm = llm_instances[model_name]
        sql = generate_sql(llm, question, schema)
        if sql:
            result = run_sql_query(sql, db_file)
            return f"**Query:**\n```sql\n{sql}\n```\n\n**Results:**\n{result}"
        logger.info("No SQL generated; falling back to web search for: %r", question)
        return format_web_summary(question, tavily_search(question, api_keys["tavily"]))

    def handle_query(dropdown: str, custom: str, model_name: str) -> str:
        query = custom.strip() if custom.strip() else dropdown
        if not query or query == "--Select--":
            return "Please select a valid question or type one."
        if is_prompt_injection(query):
            logger.warning("Blocked unsafe input in UI: %r", query)
            return "Security alert: Unsafe input detected."
        try:
            return sql_qa_pipeline(query, model_name)
        except Exception as exc:
            logger.error("Pipeline error for query %r: %s", query, exc, exc_info=True)
            return f"An error occurred while processing your request. Please try again."

    with gr.Blocks() as demo:
        gr.Markdown("## Long-term Investment Advisor")
        model_choice = gr.Radio(
            list(llm_instances.keys()), label="LLM", value=list(llm_instances.keys())[0]
        )
        dropdown_query = gr.Dropdown(
            choices=PREDEFINED_QUESTIONS, label="Select a Question", value="--Select--"
        )
        custom_query = gr.Textbox(label="Or type your question", placeholder="e.g. Top 10 ETFs by 1-year return")
        submit_btn = gr.Button("Submit", variant="primary")
        output = gr.Textbox(lines=20, label="Assistant Response")
        submit_btn.click(
            fn=handle_query,
            inputs=[dropdown_query, custom_query, model_choice],
            outputs=output,
        )
    logger.info("Gradio app built successfully")
    return demo
