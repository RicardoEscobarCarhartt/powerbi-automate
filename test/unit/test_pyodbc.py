import pyodbc
import pandas as pd

def execute_sql_query(server, database, username, password, view_name):
    # Connection string
    connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}"

    try:
        # Connect to the database
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Example query on a view
        query = f"SELECT * FROM {view_name};"

        # Execute the query
        cursor.execute(query)

        # Fetch the results into a pandas DataFrame
        df = pd.read_sql_query(query, connection)

        # Print or manipulate the DataFrame as needed
        print(df)

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close the connection
        if connection:
            connection.close()

if __name__ == "__main__":
    # Replace these values with your actual database connection details
    server = "your_server_name"
    database = "your_database_name"
    username = "your_username"
    password = "your_password"
    view_name = "your_view_name"

    # Execute the SQL query and store the result in a DataFrame
    execute_sql_query(server, database, username, password, view_name)
