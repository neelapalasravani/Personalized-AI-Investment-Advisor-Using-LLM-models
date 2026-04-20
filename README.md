# Personalized-AI-Investment-Advisor

This project is an AI-powered assistant designed to help users make informed **long-term investment decisions** using a combination of **LLMs (via ChatTogether API)** and **real-time web search (via Tavily API)**. It supports querying a historical ETF dataset using SQL and augmenting responses with live news and insights.

---

## Features

-  **Natural Language Queries** → SQL over ETF database
- **LLM Models**: Integrates Llama-3.3-70B and Mistral-7B via ChatTogether
- **Web Search Integration** using Tavily API
- **Prompt Injection Detection**
- **Meta-prompting, Prompt Chaining, and Self-reflection**
- **Gradio UI** for seamless user interaction

---

## Project Structure

```
personalized-ai-investment-advisor/
│
├── README.md               # Project overview and usage
├── LICENSE                 # Open-source license
├── requirements.txt        # Python dependencies
├── .gitignore              # Excluded files
│
├── data/
│   └── etf_dataset_sample.csv     # Sample dataset (no sensitive data)
│
├── notebooks/
│   └── Personalized_AI_Advisor.ipynb  # Development and demo notebook
│
├── src/
│   ├── llm_interface.py     # ChatTogether LLM access
│   ├── web_search.py        # Tavily search logic
│   ├── advisor_engine.py    # SQL generation, execution
│   └── utils.py             # Helpers for formatting
│
├── demo/    
│   └── screenshots/         # UI screenshots
│
├── docs/
  ├── Project_Proposal.pdf
  ├── Report.pdf
  └── Presentation_Slides.pdf

```

---

##  Setup Instructions

1. **Clone the Repo**
   ```bash
   git clone https://github.com/neelapalasravani/personalized-ai-investment-advisor.git
   cd personalized-ai-investment-advisor
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   - Copy `config/api_keys_template.yaml` to `config/api_keys.yaml`
   - Add your actual `together_api_key` and `tavily_api_key` values

4. **Launch App**
   ```bash
   python main.py
   ```

---

## Demo
-  UI Screenshot:  
  

---

## Testing Integration

This section documents the testing strategy and integration verification for the Personalized AI Investment Advisor.

- **Unit Tests**: Validate individual components such as SQL generation, LLM responses, and web search results.
- **Integration Tests**: Ensure end-to-end flow from natural language query to final investment insight.
- **CI/CD**: Automated test runs on each commit to maintain code quality and reliability.

---


## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
