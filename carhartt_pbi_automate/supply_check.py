"""This module loads supply data from the SQL server database and checks if the
supply data in the Power BI dataset is up to date."""
import os
from pathlib import Path
from typing import Union

import pyodbc
import pandas as pd
from dotenv import load_dotenv

from test.unit.test_outlook import send_email


# Load the environment variables from the .env file
load_dotenv()


class SupplyCheck:
    """This class is used to check if the supply data in the Power BI dataset
    is up to date."""

    def __init__(
        self,
        supply_excel_file: Union[Path, str] = None,
        supply_excel_sheet: str = "Sheet1",
        server: str = "DBNSQLPNET",
        database: str = "CarharttDw",
        sql_query_file: Union[Path, str] = None,
    ) -> None:
        """This method is used to initialize the object."""
        self.supply_excel_file = self.get_filepath(supply_excel_file)
        self.supply_excel_sheet = supply_excel_sheet
        self.server = server
        self.database = database
        self.sql_query_filepath = self.get_filepath(sql_query_file)

    @staticmethod
    def get_filepath(file: Union[Path, str]) -> Path:
        """This method returns the filepath if the file is valid, otherwise raises an error.
        Args:
            file (Union[Path, str]): The file to validate.
        Returns:
            Union[Path, None]: The filepath if the file is valid.
        Raises:
            ValueError: If the file is invalid."""
        # Validate the sql_query_file is valid
        if file:
            if isinstance(file, str):
                filepath = Path(file)
                if filepath.exists() and filepath.is_file():
                    return filepath
            elif isinstance(file, Path):
                if file.exists() and file.is_file():
                    return file
            else:
                raise ValueError(
                    "File must be a pathlib.Path object or a string to the file path."
                )
        raise ValueError(
            "File is required. Please use a valid pathlib.Path object or a string to the file path."
        )

    def get_excel_supply_dataframe(
        self, filename: str = None, sheet_name: str = None
    ) -> pd.DataFrame:
        """Load the excel file and store the result in a DataFrame.
        Returns:
            pandas.DataFrame: The DataFrame containing the data from the Excel file.
        """
        # If optional arguments are provided, use them to replace the default
        # values
        if filename:
            self.supply_excel_file = self.get_filepath(filename)
        if sheet_name:
            self.supply_excel_sheet = sheet_name

        # Load the excel file into a pandas DataFrame
        dataframe = pd.read_excel(
            self.supply_excel_file, sheet_name=self.supply_excel_sheet
        )

        # Filter out the grand total row
        dataframe = self.filterout_grand_total(dataframe)

        # Return the DataFrame
        return dataframe

    def get_supply_dataframe(
        self,
        server: str,
        database: str,
        sql_query_filepath: Union[Path, str] = None,
    ) -> pd.DataFrame:
        """Execute the SQL query that get's supply data from SQL server and
        store the result in a DataFrame."""
        # Connection string for Windows authentication
        connection_string = (
            f"DRIVER=ODBC Driver 17 for SQL Server;"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes"
        )

        # Validate the SQL query file path is valid
        if sql_query_filepath:
            self.sql_query_filepath = self.get_filepath(sql_query_filepath)

        # Load the SQL query from the file
        with open(sql_query_filepath, "r", encoding="utf-8") as f:
            sql_query = f.read()

        try:
            # Initialize connection to None
            connection = None

            while connection is None or not self.is_connection_successful(
                connection
            ):
                try:
                    # Connect to the database
                    connection = pyodbc.connect(
                        connection_string, readonly=True
                    )
                except Exception:
                    print(f"Error: Database connection failed. Retrying...")
                    continue

            print("Connected to the database.")
            cursor = connection.cursor()

            # Execute the query
            print("Executing query...")
            cursor.execute(sql_query)

            # Fetch the results into python list
            results = cursor.fetchall()
            print("Fetched the results.")

            # Fetch the results into a pandas DataFrame
            dataframe = pd.DataFrame.from_records(
                results, columns=[column[0] for column in cursor.description]
            )

            # Return the DataFrame
            return dataframe
        except pyodbc.Error as e:
            print(f"pyodbc.Error: {str(e)}")
        except Exception as e:
            print(f"Error: {str(e)}")

        finally:
            # Close the connection
            if connection is not None:
                connection.close()
                print("Connection closed.")

        return None

    def is_connection_successful(self, connection) -> bool:
        """Check if the connection to the database is successful.
        Args:
            connection (pyodbc.Connection): The connection to the database.
        Returns:
            bool: True if the connection is successful, False otherwise."""
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")  # Execute a simple query
            return True
        except Exception:
            return False

    def filterout_grand_total(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Filter out the grand total row from the DataFrame.
        Args:
            df (pd.DataFrame): The DataFrame to filter.
        Returns:
            pd.DataFrame: The filtered DataFrame."""
        # Filter out rows based on your criteria
        # For example, exclude rows where 'Row Labels' is not 'Grand Total'
        filtered_dataframe = dataframe[
            dataframe["Row Labels"] != "Grand Total"
        ]
        return filtered_dataframe
