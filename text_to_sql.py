import streamlit as st
import sqlite3
import sqlglot
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load GPT-2 model and tokenizer for local SQL generation
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)


# Function to set up the SQLite database and create the required tables
def setup_database():
    with sqlite3.connect('example.db', timeout=30) as conn:
        cursor = conn.cursor()

        # Drop and recreate the employees table
        cursor.execute('DROP TABLE IF EXISTS employees;')
        cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            department TEXT,
            salary REAL,
            hire_date TEXT,
            manager_id INTEGER,
            employment_type TEXT
        )
        ''')

        # Drop and recreate the customers table
        cursor.execute('DROP TABLE IF EXISTS customers;')
        cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            country TEXT
        )
        ''')

        # Drop and recreate the products table
        cursor.execute('DROP TABLE IF EXISTS products;')
        cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL,
            category TEXT
        )
        ''')

        # Insert mock data into tables
        cursor.executemany('''
        INSERT INTO employees (name, age, department, salary, hire_date, manager_id, employment_type) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('Alice', 30, 'Sales', 60000, '2015-03-15', 1, 'Full-time'),
            ('Bob', 40, 'HR', 50000, '2011-08-22', None, 'Part-time'),
            ('Charlie', 25, 'Engineering', 55000, '2020-09-17', 2, 'Full-time'),
            ('David', 35, 'Sales', 70000, '2018-11-02', 3, 'Full-time'),
            ('Eve', 45, 'Engineering', 80000, '2009-12-03', 2, 'Part-time')
        ])

        cursor.executemany('''
        INSERT INTO customers (name, age, country) VALUES (?, ?, ?)
        ''', [
            ('John', 28, 'USA'),
            ('Alice', 34, 'Canada'),
            ('Bob', 23, 'UK'),
            ('Eve', 40, 'Australia'),
            ('Charlie', 35, 'Germany')
        ])

        cursor.executemany('''
        INSERT INTO products (product_name, price, category) VALUES (?, ?, ?)
        ''', [
            ('Laptop', 1200.50, 'Electronics'),
            ('Smartphone', 850.75, 'Electronics'),
            ('Tablet', 450.00, 'Electronics'),
            ('Monitor', 220.00, 'Electronics'),
            ('Keyboard', 40.00, 'Accessories')
        ])

        conn.commit()

# Function to generate SQL using GPT-2 with improved prompting
def generate_sql_with_gpt2(query, mode):
    # Adjust the prompt based on the selected mode
    if mode == "SQL Mode":
        prompt = f"Given the following natural language query, generate a valid SQL query:\n\nQuery: {query}\n\nSQL:"
    elif mode == "Code Syntax Mode":
        prompt = f"Convert the following natural language query into a code-like SQL query:\n\nQuery: {query}\n\nSQL:"
    else:
        prompt = f"Convert the following natural language query to SQL:\n\nQuery: {query}\n\nSQL:"

    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(input_ids, max_length=150, num_return_sequences=1)
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Post-process the output to ensure it's valid SQL and clean
    sql_query = sql_query.split("SQL:")[-1].strip()  # Extract only the SQL part
    sql_query = sql_query.split(";")[0] + ";"  # Ensure we only keep the first valid SQL query
    
    if "SELECT" in sql_query.upper():
        return sql_query.strip() + ";"
    else:
        return None

# Function to generate SQL using predefined templates (fallback method)
def generate_sql_from_templates(query):
    query_lower = query.lower()
    
    if "list the names of all employees" in query_lower:
        return "SELECT name FROM employees;"
    
    elif "average salary" in query_lower and "department" in query_lower:
        # Extract department name and clean it up
        dept = query_lower.split("in the")[-1].strip().replace("department", "").strip().capitalize()
        dept = dept.replace("?", "")  # Remove any question marks or extraneous characters
        return f"SELECT AVG(salary) FROM employees WHERE department = '{dept}';"
    
    elif "salary greater than" in query_lower:
        salary_str = query_lower.split("greater than")[-1].strip().replace("$", "").replace(",", "")
        salary_str = ''.join(filter(str.isdigit, salary_str))
        if salary_str.isdigit():
            salary = int(salary_str)
            return f"SELECT * FROM employees WHERE salary > {salary};"
        else:
            return None
    
    elif "hired after" in query_lower:
        year = query_lower.split("after")[-1].strip()
        return f"SELECT name FROM employees WHERE hire_date > '{year}-01-01';"
    
    elif "highest salary" in query_lower:
        return "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
    
    elif "total salary expense" in query_lower:
        return "SELECT SUM(salary) FROM employees;"
    
    # Additional templates...
    
    return None

# Main function to generate SQL (templates first, then fallback to GPT-2)
def generate_sql(query, mode):
    sql_query = generate_sql_from_templates(query)
    if sql_query:
        return sql_query
    else:
        return generate_sql_with_gpt2(query, mode)

# Function to validate SQL using sqlglot
def validate_sql(sql_query):
    try:
        sqlglot.parse_one(sql_query)
        return True, "SQL is valid"
    except Exception as e:
        return False, str(e)

# Function to execute SQL on a SQLite database
def execute_sql(sql_query):
    if sql_query is None:
        return "Invalid SQL Query or Unable to Generate SQL"
    
    with sqlite3.connect('example.db', timeout=30) as conn:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            results = cursor.fetchall()
            conn.commit()
            return results
        except Exception as e:
            return f"SQL Execution Error: {str(e)}"

# Load the BIRD Benchmark data
def load_bird_questions():
    with open('bird_questions.json', 'r') as file:
        questions = json.load(file)
    return questions

# Benchmarking the generated SQLs against the BIRD dataset
def run_benchmark(questions, mode):
    success_count = 0
    
    for question in questions:
        st.write("-" * 50)
        st.write(f"**Question:** {question['question']}")
        generated_sql = generate_sql(question['question'], mode)
        st.write(f"**Generated SQL by Model:** {generated_sql}")
        st.write(f"**Expected SQL from BIRD Benchmark:** {question['sql']}")
        
        # Validate the generated SQL
        is_valid, validation_message = validate_sql(generated_sql)
        st.write(f"**Validation:** {validation_message}")
        
        if is_valid:
            expected_results = execute_sql(question['sql'])
            generated_results = execute_sql(generated_sql)
            st.write(f"**Expected Results:** {expected_results}")
            st.write(f"**Generated Results:** {generated_results}")
            
            if generated_results == expected_results:
                success_count += 1
                st.write("**Result: Success**")
            else:
                st.write("**Result: Mismatch in results.**")
        else:
            st.write("**Result: Invalid SQL Query.**")
    
    success_rate = (success_count / len(questions)) * 100
    st.write(f"**Overall Benchmark Success Rate:** {success_rate}%")
    return success_rate

# Streamlit interface for interaction
def main():
    st.title("Text-to-SQL Engine with BIRD Benchmark")
    
    # Set up the database
    setup_database()
    
    # Select mode
    mode = st.selectbox("Select Mode", ["SQL Mode", "Code Syntax Mode"])
    
    # Load BIRD questions
    bird_questions = load_bird_questions()
    
    # User input for testing individual queries
    user_query = st.text_input("Enter your query:")
    if st.button("Generate SQL"):
        if user_query:
            generated_sql = generate_sql(user_query, mode)
            st.write("Generated SQL:")
            st.code(generated_sql)
            
            is_valid, validation_message = validate_sql(generated_sql)
            st.write(validation_message)
            
            if is_valid:
                results = execute_sql(generated_sql)
                st.write("Execution Results:")
                st.write(results)
            else:
                st.write("Invalid SQL Query.")
    
    # Evaluate using BIRD Benchmark
    if st.button("Evaluate on BIRD Benchmark"):
        run_benchmark(bird_questions, mode)

if __name__ == "__main__":
    main()
