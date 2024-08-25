# Text-to-SQL Engine with BIRD Benchmark Evaluation

This project implements a Text-to-SQL engine that converts natural language queries into SQL queries using a GPT-2 model. The engine can be evaluated against the BIRD benchmark to measure its accuracy and performance.

---
## Features

- **Natural Language to SQL Conversion:** Generates SQL queries from natural language inputs using GPT-2.
- **Template-Based SQL Generation:** Uses predefined templates for common SQL queries.
- **BIRD Benchmark Evaluation:** Compares generated SQL queries against a set of benchmark queries from the BIRD dataset.
- **Interactive Streamlit Application:** Provides an easy-to-use interface for testing queries and evaluating the model.

---
## Directory Structure

      
      text_to_sql/
      ├── bird_benchmark.py         # Script to interface with the BIRD benchmark
      ├── text_to_sql.py            # Main Streamlit application
      ├── requirements.txt          # Dependencies
      ├── bird_questions.json       # JSON file containing BIRD benchmark questions
      └── README.md                 # Project documentation
      
- Main Application (text_to_sql.py):
This is your main Streamlit application script, which contains the logic for generating SQL from natural language queries, executing the SQL, and evaluating it against the BIRD benchmark.

- BIRD Benchmark Script (bird_benchmark.py):
A script dedicated to handling the loading and processing of the BIRD benchmark data. This script could be integrated into text_to_sql.py if desired, but keeping it separate helps in modularity.

- Dependencies (requirements.txt):
This file lists all the Python packages required for your project.

      streamlit
      transformers
      sqlglot
      sqlite3

- BIRD Questions (bird_questions.json):
This JSON file contains the questions and expected SQL queries that make up the BIRD benchmark. Ensure this file is in the root directory of your project.

---
## Installation

- **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/text_to_sql.git
   cd text_to_sql

  pip install -r requirements.txt  
  
  streamlit run text_to_sql

---

## Result

<p align = 'left'>
  <img src = 'utils/Screenshot 2024-08-25 161936.png' align = 'center'>
</p>

<p align = 'left'>
  <img src = 'utils/Screenshot 2024-08-25 161706.png' align = 'center'>
</p>

<p align = 'left'>
  <img src = 'utils/Screenshot 2024-08-25 161738.png' align = 'center'>
</p>
