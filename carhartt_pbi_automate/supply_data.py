"""This module loads supply data from the SQL server database and checks if the
supply data in the Power BI dataset is up to date."""
import os
from pathlib import Path
from typing import Union
import logging

import pyodbc
import pandas as pd
from dotenv import load_dotenv

from test.unit.test_outlook import send_email
from carhartt_pbi_automate.my_logger import MyLogger


# Load the environment variables from the .env file
load_dotenv()

# Create a logger object, used to log messages in the console, a file and a
# database
log = MyLogger(
    name="carhartt_pbi_automate.supply_data",
    log_file=Path("logs/supply_data.log"),
    level=logging.INFO,
    log_to_console=True,
    log_to_file=True,
    log_to_database=True,
    database=Path("database/logging.db"),
)


class SupplyData:
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
        server: str = None,
        database: str = None,
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

        # Validate the optional arguments if provided
        if server:
            self.server = server
        if database:
            self.database = database
        if sql_query_filepath:
            self.sql_query_filepath = self.get_filepath(sql_query_filepath)

        # Load the SQL query from the file
        with open(self.sql_query_filepath, "r", encoding="utf-8") as f:
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
                except pyodbc.Error:
                    log.error(
                        "Error: Database connection failed. Retrying...\n"
                    )
                    continue
                except Exception as e:
                    log.critical(
                        "Critical: Database connection failed. %s", str(e)
                    )
                    break

            log.info("Connected to the database.")
            cursor = connection.cursor()

            # Execute the query
            log.info("Executing query...")
            cursor.execute(sql_query)

            # Fetch the results into python list
            results = cursor.fetchall()
            log.info("Fetched the results.")

            # Fetch the results into a pandas DataFrame
            dataframe = pd.DataFrame.from_records(
                results, columns=[column[0] for column in cursor.description]
            )

            # Return the DataFrame
            return dataframe
        except pyodbc.Error as e:
            log.error("pyodbc.Error: %s", {str(e)})
        except Exception as e:
            log.critical("Critical: %s", str(e))

        finally:
            # Close the connection
            if connection is not None:
                connection.close()
                log.info("Connection closed.")

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
        except pyodbc.Error:
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

    def check(self):
        """Check comparing that the Excel file and the SQL query return the
        same dataset. If there are differences, send an email."""
        # Harcoded column names for now
        excel_column_names = [
            "Row Labels",
            "Sales Demand Units",
            "Total Receipt Plan Units",
            "Planned Production Units",
        ]
        database_column_names = [
            "YearPeriodMonth",
            "SalesDemandUnits",
            "TotalReceiptPlanUnits",
            "PlannedProductionUnits",
        ]

        # Get the supply data from the excel file and store it in a DataFrame
        excel_dataframe = self.get_excel_supply_dataframe()

        # Get the supply data from the database and store it in a DataFrame
        database_dataframe = self.get_supply_dataframe()

        # Database dataframe
        excel_series = []
        database_series = []

        # Strip whitespace from the string columns
        for column_name in excel_column_names:
            if (
                excel_dataframe[column_name].dtype == "object"
            ):  # 'object' typically means strings in pandas
                excel_series.append(excel_dataframe[column_name].str.strip())
            else:
                excel_series.append(excel_dataframe[column_name])

        for column_name in database_column_names:
            if (
                database_dataframe[column_name].dtype == "object"
            ):  # 'object' typically means strings in pandas
                database_series.append(
                    database_dataframe[column_name].str.strip()
                )
            else:
                database_series.append(database_dataframe[column_name])

        # Create a list of tuples of the excel and database series
        # to iterate over them and assert the equality of the columns
        for excel_column, database_column in zip(
            excel_series, database_series
        ):
            try:
                # Assert the equality of the columns
                pd.testing.assert_series_equal(
                    excel_column,
                    database_column,
                    check_dtype=False,
                    check_index=False,
                    check_series_type=False,
                    check_names=False,
                )
            except AssertionError:
                # Send an email with the difference
                email_database_dataframe = pd.DataFrame(
                    {
                        "YearPeriodMonth": database_dataframe[
                            "YearPeriodMonth"
                        ],
                        "SalesDemandUnits": database_dataframe[
                            "SalesDemandUnits"
                        ],
                        "TotalReceiptPlanUnits": database_dataframe[
                            "TotalReceiptPlanUnits"
                        ],
                        "PlannedProductionUnits": database_dataframe[
                            "PlannedProductionUnits"
                        ],
                    }
                )
                send_email(
                    subject="Supply Data Mismatch",
                    body="<p><b>Database:</b>\n\nRepresents what's currently on the database and it's expected to be in PowerBI as well.</p><p><b>PowerBI:</b>\n\nRepresents what's currently in the Excel file exported from a PowerBI dataset and is currently different from the Database data.",
                    to_address=os.getenv("OUTLOOK_RECIPIENT_EMAIL"),
                    database_dataframe=email_database_dataframe,
                    powerbi_dataframe=excel_dataframe,
                )
            else:
                log.info("OK: There is no difference.")


if __name__ == "__main__":
    # Create an instance of the SupplyData class
    EXCEL_FILE = Path(
        "data/Excel para automatización/Sin conexión a Supply-solo datos.xlsx"
    )
    SQL_FILE = Path("sql/supply.sql")
    supply_data = SupplyData(
        supply_excel_file=EXCEL_FILE, sql_query_file=SQL_FILE
    )

    # Check if the supply data in the Power BI dataset is up to date
    supply_data.check()
