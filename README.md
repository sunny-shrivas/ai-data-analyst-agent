# AI Data Analyst

An interactive CSV analysis application built with **Python, Pandas, Plotly, and Streamlit**, with optional OpenAI-powered natural-language answers. Upload a dataset, inspect its quality, explore numeric and categorical data, and ask questions about the results.

## Features

- Upload a CSV or use the included sales dataset.
- Dataset overview: dimensions, column types, sample values, and preview.
- Data quality checks: missing cells, duplicate rows, and a missing-value chart.
- Deterministic observations for numeric and categorical columns.
- Interactive bar, line, scatter, histogram, and box charts.
- Optional AI answers grounded in aggregate dataset statistics.
- Download the loaded dataset as CSV.

## Project structure

    ai-data-analyst-agent/
    ├── main.py
    ├── agent.py
    ├── tools.py
    ├── dataset.csv
    ├── tests/
    │   └── test_tools.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md

## Quick start

Clone the repository:

    git clone https://github.com/sunny-shrivas/ai-data-analyst-agent.git
    cd ai-data-analyst-agent

Create and activate a virtual environment.

**macOS / Linux**

    python3 -m venv .venv
    source .venv/bin/activate

**Windows PowerShell**

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install --upgrade pip
    pip install -r requirements.txt

Run the app:

    streamlit run main.py

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Optional AI answers

Set the following environment variables locally or in your deployment platform:

    OPENAI_API_KEY=your_key_here
    OPENAI_MODEL=gpt-4o-mini

The app does not load .env automatically. Export the variables in your shell or use your hosting platform's secrets manager. Never commit real API keys.

Without an API key, CSV loading, profiling, quality checks, charts, and deterministic insights continue to work. When AI is enabled, the app sends the dataset schema and aggregate statistics to the configured OpenAI model, not the raw CSV rows. Do not submit sensitive data unless you are comfortable with that processing.

## Tests

    pytest -q

## Security and limitations

- The app does not execute user-provided Python, SQL, or shell commands.
- Uploaded files are processed in memory during the app session.
- CSV is currently the supported input format.
- Data cleaning is diagnostic only; the source dataset is not modified in place.
- AI answers depend on the supplied aggregate context and may be incomplete. Verify important conclusions against the displayed data.
- No model accuracy score is claimed: this is an exploratory analysis assistant, not a predictive model.

## Roadmap

- Excel and JSON ingestion.
- Reversible cleaning actions and cleaned-data export.
- SQL/database connectors using parameterized queries.
- Statistical tests and anomaly detection.
- Evidence-linked answers that reference computed metrics.
- Continuous integration and deployment workflow.

## Author

**Sunny Shrivas** · [GitHub](https://github.com/sunny-shrivas)
