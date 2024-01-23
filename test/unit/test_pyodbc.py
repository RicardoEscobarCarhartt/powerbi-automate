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


def get_excel_supply_dataframe(
    filename: Union[Path, str] = None, sheet_name: str = "Sheet1"
) -> pd.DataFrame:
    """Load the excel file and store the result in a DataFrame.
    Args:
        filename (Union[Path, str], optional): The path to the Excel file. Defaults to None.
    Raises:
        ValueError: If filename is None.
        ValueError: If filename is not a string or Path object.
    Returns:
        pd.DataFrame: The DataFrame containing the data from the Excel file."""
    # Validate the filename is valid
    if filename:
        if isinstance(filename, str):
            filename = Path(filename)
        if not isinstance(filename, Path):
            raise ValueError(
                "Filename must be a pathlib.Path object or a string to the file path."
            )
    else:
        raise ValueError(
            "Filename is required. Please use a valid pathlib.Path object or a string to the file path."
        )

    # Load the excel file into a pandas DataFrame
    df = pd.read_excel(filename, sheet_name=sheet_name)

    # Filter out the grand total row
    df = filterout_grand_total(df)

    # Print or manipulate the DataFrame as needed
    print(df)

    # Return the DataFrame
    return df


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
        # Initialize connection to None
        connection = None

        try:
            # Connect to the database
            connection = pyodbc.connect(connection_string, readonly=True)
            print("Connected to the database.")
        except pyodbc.Error as e:
            print(f"pyodbc.Error: Database connection failed. {str(e)}")
            raise e

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
    excel_str = (
        "data/Excel para automatización/Sin conexión a Supply-solo datos.xlsx"
    )

    server = os.getenv("SERVER")
    database = os.getenv("DATABASE")
    sql_filepath = Path("sql/supply.sql")
    excel_filepath = Path(excel_str)

    try:
        # Get the supply data from the excel file and store it in a DataFrame
        excel_df = get_excel_supply_dataframe(excel_filepath, "Sheet1")

        # Get the supply data from the database and store it in a DataFrame
        supply_df = get_supply_dataframe(server, database, sql_filepath)
    except FileNotFoundError as error:
        print(f"FileNotFoundError: {str(error)}")
    except ValueError as error:
        print(f"ValueError: {str(error)}")
    except Exception as error:
        print(f"Error: {str(error)}")

    # Assert the '[YearPeriodMonth]' column in the supply_df is equal to the
    # 'Row Labels' column in the excel_df. Excluding the column names.
    try:
        # Extract the relevant columns and clean them for comparison
        # SQL columns
        supply_dates = supply_df["YearPeriodMonth"].str.strip()
        supply_sales_demand_units = supply_df["SalesDemandUnits"]
        supply_total_receipt_plan_units = supply_df["TotalReceiptPlanUnits"]
        supply_planned_production_units = supply_df["PlannedProductionUnits"]

        # Excel columns
        excel_dates = excel_df["Row Labels"].str.strip()
        excel_sales_demand_units = excel_df["Sales Demand Units"]
        excel_total_receipt_plan_units = excel_df["Total Receipt Plan Units"]
        excel_planned_production_units = excel_df["Planned Production Units"]

        # Assert the equality of the dates columns
        pd.testing.assert_series_equal(
            supply_dates,
            excel_dates,
            check_dtype=False,
            check_index=False,
            check_series_type=False,
            check_names=False,
        )
        # Assert the equality of the sales demand units columns
        pd.testing.assert_series_equal(
            supply_sales_demand_units,
            excel_sales_demand_units,
            check_dtype=False,
            check_index=False,
            check_series_type=False,
            check_names=False,
        )
        # Assert the equality of the Total Receipt Plan Units columns
        pd.testing.assert_series_equal(
            supply_total_receipt_plan_units,
            excel_total_receipt_plan_units,
            check_dtype=False,
            check_index=False,
            check_series_type=False,
            check_names=False,
        )
        # Assert the equality of the Planned Production Units columns
        pd.testing.assert_series_equal(
            supply_planned_production_units,
            excel_planned_production_units,
            check_dtype=False,
            check_index=False,
            check_series_type=False,
            check_names=False,
        )
    except Exception as exeption:
        # Calculate the difference between the actual and expected values
        difference_row_labels = supply_df["YearPeriodMonth"].compare(
            excel_df["Row Labels"]
        )
        difference_sales_demand_units = supply_df["SalesDemandUnits"].compare(
            excel_df["Sales Demand Units"]
        )
        difference_total_receipt_plan_units = supply_df[
            "TotalReceiptPlanUnits"
        ].compare(excel_df["Total Receipt Plan Units"])
        difference_planned_production_units = supply_df[
            "PlannedProductionUnits"
        ].compare(excel_df["Planned Production Units"])
        
        if not difference_row_labels.empty:
            # Rename the columns
            difference_row_labels.columns = ["Database", "Excel"]
            print(
                f"Row Labels: {exeption}\nThere is difference of:\n{difference_row_labels}"
            )
        if not difference_sales_demand_units.empty:
            # Rename the columns
            difference_sales_demand_units.columns = ["Database", "Excel"]
            print(
                f"Sales Demand Units: {exeption}\nThere is difference of:\n{difference_sales_demand_units}"
            )
        if not difference_total_receipt_plan_units.empty:
            # Rename the columns
            difference_total_receipt_plan_units.columns = ["Database", "Excel"]
            print(
                f"Total Receipt Plan Units: {exeption}\nThere is difference of:\n{difference_total_receipt_plan_units}"
            )
        if not difference_planned_production_units.empty:
            # Rename the columns
            difference_planned_production_units.columns = ["Database", "Excel"]
            print(
                f"Planned Production Units: {exeption}\nThere is difference of:\n{difference_planned_production_units}"
            )

        # TODO: Send an email with the difference
    else:
        print("OK: There is no difference.")


if __name__ == "__main__":
    main()
