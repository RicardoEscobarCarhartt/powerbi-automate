"""This module tests the pyodbc library being used to connect to the database
and execute the query. The results are then stored in a pandas DataFrame."""
import os
from pathlib import Path
from typing import Union

import pyodbc
import pandas as pd
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()


def get_supply_dataframe(
    server: str, database: str, sql_query_filepath: Union[Path, str] = None
) -> pd.DataFrame:
    """Execute the SQL query that get's supply data from SQL server and store
    the result in a DataFrame."""
    # Connection string for Windows authentication
    connection_string = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes"

    # Validate the SQL query file path is valid
    if sql_query_filepath:
        if isinstance(sql_query_filepath, str):
            sql_query_filepath = Path(sql_query_filepath)
        if not isinstance(sql_query_filepath, Path):
            raise ValueError(
                "SQL query file path must be a pathlib.Path object or a string to the file path."
            )
    else:
        raise ValueError(
            "SQL query file path is required. Please use a valid pathlib.Path object or a string to the file path."
        )

    # Load the SQL query from the file
    with open(sql_query_filepath, "r", encoding="utf-8") as f:
        sql_query = f.read()

    try:
        # Connect to the database
        connection = pyodbc.connect(connection_string, readonly=True)
        print("Connected to the database.")
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(sql_query)
        print("Executed the query.")

        # Fetch the results into python list
        results = cursor.fetchall()
        print("Fetched the results.")

        # Fetch the results into a pandas DataFrame
        df = pd.DataFrame.from_records(
            results, columns=[column[0] for column in cursor.description]
        )

        # Print or manipulate the DataFrame as needed
        print(df)

        # Return the DataFrame
        return df
    except pyodbc.Error as e:
        print(f"pyodbc.Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close the connection
        if connection is not None:
            connection.close()
            print("Connection closed.")


def filterout_grand_total(df) -> pd.DataFrame:
    """Filter out the grand total row from the DataFrame.
    Args:
        df (pd.DataFrame): The DataFrame to filter.
    Returns:
        pd.DataFrame: The filtered DataFrame."""
    # Filter out rows based on your criteria
    # For example, exclude rows where 'Row Labels' is not 'Grand Total'
    df_filtered = df[df["Row Labels"] != "Grand Total"]
    return df_filtered


def main():
    """Main function"""
    # Replace these values with your actual database connection details
    server = os.getenv("SERVER")
    database = os.getenv("DATABASE")
    sql_filepath = Path("sql/supply.sql")

    # Execute the SQL query and store the result in a DataFrame
    supply_df = get_supply_dataframe(server, database, sql_filepath)


if __name__ == "__main__":
    main()
