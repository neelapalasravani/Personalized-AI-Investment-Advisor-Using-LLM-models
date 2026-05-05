import logging
import gradio as gr
from src.llm_interface import get_llm_instances
from src.web_search import tavily_search
from src.advisor_engine import generate_sql, run_sql_query, is_prompt_injection
from src.utils import format_web_summary

logger = logging.getLogger(__name__)

def build_app(schema, db_file, api_keys):
    try:
        llm_instances = get_llm_instances(api_keys["together"])
    except KeyError:
        logger.error("Missing 'together' API key in configuration.")
        raise

    def sql_qa_pipeline(question, model_name):
        try:
            llm = llm_instances[model_name]
        except KeyError:
            logger.error(f"Unknown or unavailable model: {model_name}")
            return f"Error: Model '{model_name}' is not available."

        try:
            sql = generate_sql(llm, question, schema)
            if sql:
                result = run_sql_query(sql, db_file)
                return f"**Query:**\n```sql\n{sql}\n```\n\n**Results:**\n{result}"
        except Exception as e:
            logger.error(f"SQL generation/execution error: {e}")
            return f"An error occurred while processing your question: {e}"

        try:
            web_results = tavily_search(question, api_keys["tavily"])
            return format_web_summary(question, web_results)
        except KeyError:
            logger.error("Missing 'tavily' API key in configuration.")
            return "Web search is unavailable: missing API key."
        except Exception as e:
            logger.error(f"Web search fallback failed: {e}")
            return f"Web search error: {e}"

    def handle_query(dropdown, custom, model_name):
        query = custom.strip() if custom.strip() else dropdown
        if query == "--Select--" or not query:
            return "Please select a valid question or type one."
        if is_prompt_injection(query):
            return "Security alert: Unsafe input detected."
        return sql_qa_pipeline(query, model_name)

    with gr.Blocks() as demo:
        gr.Markdown("## Long-term Investment Advisor")
        model_choice = gr.Radio(["Llama-3.3-70B", "Mistral-7B"], label="LLM", value="Llama-3.3-70B")
        dropdown_query = gr.Dropdown(choices=["--Select--", "Top 5 ETFs by price", "Latest news about ETF market"], label="Select a Question")
        custom_query = gr.Textbox(label="Or type your question")
        submit = gr.Button("Submit")
        output = gr.Textbox(lines=20, label="Assistant Response")
        submit.click(fn=handle_query, inputs=[dropdown_query, custom_query, model_choice], outputs=output)
    return demo
