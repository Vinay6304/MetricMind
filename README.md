MetricMind

MetricMind is a sales analytics dashboard that combines Snowflake, Flask, Chart.js, and a rule-based AI insight engine to analyze business performance.

The system retrieves live sales data from Snowflake, calculates business metrics, displays them through an interactive dashboard, and provides natural-language business insights.

## Features

- Interactive sales analytics dashboard
- Live data retrieval from Snowflake
- Revenue, cost, profit, orders, and profit-margin analysis
- Country-wise analysis
- Product-wise analysis
- Region-wise analysis
- Monthly sales analysis
- Region filtering
- Interactive charts using Chart.js
- AI-powered business questions through the "/api/ai" endpoint
- Automatic AI summary through "/api/ai/summary"
- Comparisons between products, countries, and other dashboard entities
- Ranking analysis
- Trend analysis
- Profit-margin analysis
- Secure environment-variable based configuration
- Git-based project version control

## Technology Stack

### Backend

- Python
- Flask
- Flask-CORS
- Snowflake Connector for Python
- Pandas
- NumPy
- python-dotenv

### AI

MetricMind currently uses a mock/rule-based AI mode.

This was intentionally selected instead of continuously calling the OpenAI API because OpenAI API usage requires paid credits.

The project retains optional OpenAI/LangChain integration in the code, but the normal project configuration uses:

METRICMIND_AI_MODE=mock

This allows the AI analysis functionality to operate without API charges.

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js

### Data Platform

- Snowflake
- Cube-related project components

## Project Structure

MetricMind/
├── backend/
│   ├── app.py
│   └── scripts/
│       ├── ai_service.py
│       ├── analytics.py
│       ├── cube_schema.py
│       ├── cube_service.py
│       └── load_data.py
│
├── cube/
│   └── model/
│       └── schema.yml
│
├── cube-test/
│
├── data/
│   └── raw/
│       └── sales.csv
│
├── dbt/
├── docs/
│
├── frontend/
│   └── index.html
│
├── .env
├── .gitignore
├── package.json
├── package-lock.json
├── requirements.txt
└── README.md

## Environment Configuration

Create a ".env" file in the project root.

The file should contain the required Snowflake configuration:

SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_ROLE=your_role

For the current AI configuration:

METRICMIND_AI_MODE=mock

If OpenAI mode is intentionally enabled in the future, the corresponding API key must be supplied through an environment variable rather than committed to Git.

Never commit ".env" or API keys to the repository.

## Installation

Create and activate a Python virtual environment.

Windows PowerShell

python -m venv venv
.\venv\Scripts\Activate.ps1

Install the Python dependencies:

python -m pip install -r requirements.txt

Verify the environment:

python -m pip check

A successful environment should report:

No broken requirements found.

## Running MetricMind

From the project root:

.\venv\Scripts\Activate.ps1
python backend\app.py

The Flask development server should start on:

http://127.0.0.1:5000

API Health Endpoint

http://127.0.0.1:5000/

Dashboard

http://127.0.0.1:5000/dashboard

## API Endpoints

Dashboard

GET /api/dashboard

Returns dashboard analytics data.

Optional region filtering:

GET /api/dashboard?region=Asia

AI Question

POST /api/ai

Example request:

{
  "prompt": "Which product has the highest profit?"
}

A region can also be supplied:

{
  "prompt": "Which product has the highest profit?",
  "region": "Asia"
}

Automatic AI Summary

GET /api/ai/summary

Optional region filtering:

GET /api/ai/summary?region=Asia

The summary includes:

- Total orders
- Total revenue
- Total cost
- Total profit
- Profit margin
- Top country
- Top product
- Top profit-producing product
- Top region
- Best month
- Weakest month

Cube Dashboard

GET /api/cube-dashboard

Returns dashboard data through the Cube-related service.

## Example AI Questions

MetricMind can answer questions such as:

- What is the overall sales performance?
- Which region has the highest profit?
- Compare Laptop and Keyboard by profit.
- Rank all countries by revenue.
- Is profit increasing or decreasing over time?
- Which product has the highest profit margin?

## Example Results

Example results from the current dataset include:

- Total revenue: ₹109,500
- Total cost: ₹69,700
- Total profit: ₹39,800
- Profit margin: 36.35%
- Highest-profit region: Europe — ₹15,500
- Highest-profit product: Laptop — ₹23,800
- Highest product profit margin: Keyboard — 41.90%

## Security

Sensitive configuration is stored in ".env".

The repository ignores:

.env
venv/
__pycache__/
*.pyc
node_modules

Credentials and API keys should never be placed directly into source code or committed to Git.

## Development Status

MetricMind currently has the following major components working:

- Snowflake data connection
- Dashboard analytics
- Region filtering
- Flask API
- Interactive frontend dashboard
- Chart visualizations
- AI question endpoint
- AI automatic summary
- Rule-based/mock AI analysis
- Product/country/region comparisons
- Rankings
- Trend analysis
- Git repository and dependency management

The remaining work focuses on final production-readiness checks, edge-case handling, documentation refinement, end-to-end testing, and final project verification.

## License

This project is developed as part of an internship project.