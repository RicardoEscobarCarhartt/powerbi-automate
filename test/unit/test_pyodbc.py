"""This module tests the pyodbc library being used to connect to the database
and execute the query. The results are then stored in a pandas DataFrame."""
import os

import pyodbc
import pandas as pd
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()


def execute_sql_query(server, database, view_name):
    # Connection string for Windows authentication
    connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes"

    try:
        # Connect to the database
        connection = pyodbc.connect(connection_string)
        print("Connected to the database.")
        cursor = connection.cursor()

        # Example query on a view
        query = f"SELECT * FROM {view_name};"

        # Execute the query
        cursor.execute(query)
        print("Executed the query.")

        # Fetch the results into python list
        results = cursor.fetchall()
        print("Fetched the results.")

        # Fetch the results into a pandas DataFrame
        df = pd.DataFrame.from_records(results, columns=[column[0] for column in cursor.description])

        # Print or manipulate the DataFrame as needed
        print(df.head(10))

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close the connection
        if connection:
            connection.close()


def main():
    """Main function"""
    # Replace these values with your actual database connection details
    server = os.getenv("SERVER")
    database = os.getenv("DATABASE")
    view_name = os.getenv("VIEW_NAME")

    # Execute the SQL query and store the result in a DataFrame
    execute_sql_query(server, database, view_name)


if __name__ == "__main__":
    main()
