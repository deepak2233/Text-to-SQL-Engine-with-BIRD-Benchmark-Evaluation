import json
import sqlite3

class BirdBenchmark:
    def __init__(self, database_path='example.db'):
        self.database_path = database_path
        self.questions = self.load_bird_questions()

    def load_bird_questions(self):
        """
        Load the BIRD benchmark questions from a JSON file.
        """
        with open('bird_questions.json', 'r') as file:
            questions = json.load(file)
        return questions

    def get_random_questions(self, num_questions):
        """
        Return a specified number of random questions from the BIRD benchmark.
        """
        return random.sample(self.questions, num_questions)

    def get_expected_result(self, question):
        """
        Return the expected result for a given question by executing the associated SQL query.
        """
        sql_query = question['sql']
        return self.execute_sql(sql_query)

    def execute_sql(self, sql_query):
        """
        Execute a SQL query against the SQLite database and return the results.
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute(sql_query)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            return str(e)

    def evaluate_sql(self, generated_sql, expected_results):
        """
        Compare the generated SQL query's results with the expected results.
        """
        generated_results = self.execute_sql(generated_sql)
        return generated_results == expected_results

    def run_benchmark(self, generated_sqls):
        """
        Run the benchmark for a set of generated SQL queries, comparing them to expected results.
        """
        success_count = 0
        for question, generated_sql in zip(self.questions, generated_sqls):
            expected_results = self.get_expected_result(question)
            if self.evaluate_sql(generated_sql, expected_results):
                success_count += 1
            else:
                print(f"Failed for question: {question['question']}")
                print(f"Generated SQL: {generated_sql}")
                print(f"Expected SQL: {question['sql']}")
                print(f"Expected Results: {expected_results}")
                print(f"Generated Results: {self.execute_sql(generated_sql)}")
                print("-" * 50)
        success_rate = (success_count / len(generated_sqls)) * 100
        return success_rate
