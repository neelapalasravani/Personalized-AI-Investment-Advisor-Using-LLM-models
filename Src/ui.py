import gradio as gr
from src.llm_interface import get_llm_instances
from src.web_search import tavily_search
from src.Main_pipeline import generate_sql, run_sql_query, is_prompt_injection
from src.utils import format_web_summary

def build_app(schema, db_file, api_keys):
    llm_instances = get_llm_instances(api_keys["together"])
    
    def sql_qa_pipeline(question, model_name):
        llm = llm_instances[model_name]
        sql = generate_sql(llm, question, schema)
        if sql:
            result = run_sql_query(sql, db_file)
            return f"**Query:**\n```sql\n{sql}\n```\n\n**Results:**\n{result}"
        return format_web_summary(question, tavily_search(question, api_keys["tavily"]))

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
