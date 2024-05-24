"""This module contains the main code for the Carhartt Power BI Automation
project."""

import os
import time
from datetime import datetime
import threading
from typing import List
from pathlib import Path
import traceback
import argparse

import pandas as pd
import datacompy
import pymsteams
import adodbapi
from dotenv import load_dotenv

from connector import get_edw_connection, get_bi_connection
from popup import detect_popup_window
from supply import get_edw_start_end_dates, trim_dax_columns
from get_logger import get_logger
from dax import pass_args_to_dax_query
from parse_arguments import parse_arguments
from get_formated_duration import get_formated_duration

# Create a logger object
log = get_logger("carhartt_pbi_automate", "logs/carhartt_pbi_automate.log")

# Load environment variables from .env file
load_dotenv()

# Define a global variable to store the connection to Power BI
# To be accessed from a thread.
conn_BI_result: List[adodbapi.Connection] = [None]

# Parse script arguments
try:
    script_args = parse_arguments()
    log.debug(f"Script arguments: {script_args}")
    log.debug(f"DAX file path: {script_args.daxfile}")
    log.debug(f"SQL file path: {script_args.sqlfile}")
except argparse.ArgumentError as error:
    stack_trace = traceback.format_exc()
    log.error(f"Error: {error}")
    log.error(f"Stack trace: {stack_trace}")
    log.critical("Failed to parse script arguments. Exiting the program.")
    exit(1)


# Define a function that wraps get_bi_connection.
def get_connection():
    """
    Get the connection to Power BI. This function is called from a Thread.
    That's why the connection is saved in a list to be accessed, rather than
    returned.
    """
    conn_BI = get_bi_connection(
        "powerbi://api.powerbi.com/v1.0/myorg/BI-Datasets", "Supply"
    )
    # Save the result in the list
    conn_BI_result[0] = conn_BI


log.debug(
    f"Starting the process {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Connect to the EDW database.
log.info("Connecting to EDW...")
while True:
    try:
        conn_EDW = get_edw_connection("DBNSQLPNET")
        log.info("Connection to EDW has been established!")
        break
    except Exception as error:
        stack_trace = traceback.format_exc()
        log.error(f"Error: {error}")
        log.error(f"Stack trace: {stack_trace}")
        log.info("Trying to connect again...")
        continue

# Connect to Power BI database.
is_powerbi_logged_in = False
retry_count = 3
while True:
    try:
        # Create a thread for get_connection
        thread1 = threading.Thread(target=get_connection)

        # Start the thread
        thread1.start()

        # Wait for the pop-up to appear (adjust as needed)
        log.info("Waiting for the pop-up to appear...")
        time.sleep(4)

        # Check if the pop-up window has been detected
        printed_once = False
        while not is_powerbi_logged_in:
            try:
                # Check if the connection has been established
                if conn_BI_result[0] is not None:
                    break
                # Call detect_popup_window while get_connection is running in the other thread
                detect_popup_window(".*Sign in to your account.*")
                is_powerbi_logged_in = True
            except Exception as error:
                time.sleep(2)
                if printed_once:
                    break
                else:
                    stack_trace = traceback.format_exc()
                    log.error(f"Error: {error}")
                    log.error(f"Stack trace: {stack_trace}")
                    log.info("Trying to log in again...")
                    printed_once = True

        # Wait for the thread to finish
        thread1.join()

        # Get the connection from the list
        conn_BI = conn_BI_result[0]
        break
    except Exception as error:
        stack_trace = traceback.format_exc()
        log.error(f"Error: {error}")
        log.error(f"Stack trace: {stack_trace}")
        if retry_count:
            log.info("Trying to connect again...")
            retry_count -= 1
            continue
        else:
            stack_trace = traceback.format_exc()
            log.critical(
                "Failed to connect. Exiting the program. Please check the logs for more information."
            )
            log.critical(f"Stack trace: {stack_trace}")
            exit(1)

log.info("Connection to Power BI has been established!")

# Define the webhook URL for Microsoft Teams
teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)
log.info("Connection to Teams has been established!")

# Load supply.sql file and read the query
time_start = datetime.now()
log.info("Extracting data from EDW...")
supply_sql_filepath = Path(script_args.sqlfile)
with open(supply_sql_filepath, "r", encoding="utf-8") as file:
    query_edw = file.read()
    df_edw = pd.read_sql(query_edw, conn_EDW)
time_end = datetime.now()
time_diff = time_end - time_start

# Calculate the time taken to extract data from EDW
formated_duration = get_formated_duration(time_diff)

# Print the time taken to extract data from EDW
log.info("Data from EDW has been extracted.")
log.debug(f"It took: {formated_duration} to extract data from EDW.")

# Extract data from Power BI
cursor_data_BI = conn_BI.cursor()

try:
    inventory_plans_start_month, inventory_plans_end_month = (
        get_edw_start_end_dates(df_edw)
    )
    # Get the current date in the format "NIGHTLY-MM/DD/YYYY"
    log.debug(f"Start month: {inventory_plans_start_month}")
    log.debug(f"End month: {inventory_plans_end_month}")
except ValueError as error:
    stack_trace = traceback.format_exc()
    # Send a message to Teams
    myTeamsMessage.summary("Data comparison failed")
    myTeamsMessage.text(f"Error: {error}")
    myTeamsMessage.text(
        f"""<font color='red'>Error: {error}</font><br>
        There could be an outage in the EDW database.<br>
        Please check the logs for more information.<br>
        """
    )
    myTeamsMessage.send()

    log.critical(f"Data comparison failed: {error}")
    log.critical(f"Stack trace: {stack_trace}")
    exit(1)


now = datetime.now()
plan_versions = f'"NIGHTLY-{now.month}/{now.day}/{now.year}"'
log.debug(f"Plan_versions: {plan_versions}")

# Load the DAX query from file
dax_query = Path(script_args.daxfile).read_text(encoding="utf-8")

# Pass the arguments to the DAX query
args = {
    "inventory_plans_start_month": inventory_plans_start_month,
    "inventory_plans_end_month": inventory_plans_end_month,
    "plan_versions": plan_versions,
}

dax_query = pass_args_to_dax_query(dax_query, args)

log.info("Extracting data from Power BI...")
time_start = datetime.now()

# Execute the DAX query
try:
    cursor_data_BI.execute(dax_query)
    results_table = cursor_data_BI.fetchall()
except Exception as error:
    stack_trace = traceback.format_exc()

    # Send a message to Teams
    myTeamsMessage.summary("Data comparison failed")
    myTeamsMessage.text(f"Error: {error}")
    myTeamsMessage.text(
        f"""<font color='red'>Error: {error}</font><br>
        There could be an outage in the Power BI database.<br>
        Please check the logs for more information.<br>
        """
    )
    myTeamsMessage.send()

    log.critical(f"Data comparison failed: {error}")
    log.critical(f"Stack trace: {stack_trace}")
    exit(1)

# Get the column names from the cursor, remove the brackets and create a list
column_names = [
    column[0].replace("[", "").replace("]", "")
    for column in cursor_data_BI.description
]

# Create a dataframe from the results
data_table = list(results_table)
df_pbi = pd.DataFrame(data_table, columns=column_names)
cursor_data_BI.close()
time_end = datetime.now()
time_diff = time_end - time_start

# Calculate the time taken to extract data from Power BI
formated_duration = get_formated_duration(time_diff)
log.info("Data from Power BI has been extracted!")
log.debug(f"Time to extract data from Power BI: {formated_duration}")

# Remove uneccesary the columns in the power bi dataframe,
# rename the column Year/Period/Month to YearPeriodMonth
df_pbi = trim_dax_columns(df_pbi)

# Apply ORDER BY YearPeriodMonth on both dataframes
df_pbi = df_pbi.sort_values(by="YearPeriodMonth").reset_index(drop=True)
df_edw = df_edw.sort_values(by="YearPeriodMonth").reset_index(drop=True)

# Use the datacompy library to compare the dataframes
compare = datacompy.Compare(df_pbi, df_edw, on_index=True)
compare.matches(ignore_extra_columns=False)
result = compare.all_mismatch()
result_html = result.to_html(index=False)

# Generate a timestamp to use in the result file name
timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Create results/timestamp folder if it does not exist
results_path = Path("results") / timestamp
results_path.mkdir(parents=True, exist_ok=True)

# Create the comparison result file
result_file = results_path / "comparison_result.html"

# Save the dataframes to csv files
edw_path = results_path / "edw_data.csv"
bi_path = results_path / "bi_data.csv"
df_edw.to_csv(edw_path, index=False)
log.debug(f'EDW data has been saved to "{edw_path.resolve()}"')
df_pbi.to_csv(bi_path, index=False)
log.debug(f'Power BI data has been saved to "{bi_path.resolve()}"')

# Save the comparison result to a file
with open(result_file, "w", encoding="utf-8") as file:
    file.write(result_html)
    log.debug(f'Comparison result has been saved to "{result_file.resolve()}"')

# Create the connectorcard object
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)

# If the comparation its ok do nothing, if not send a notification to the channel in teams
if compare.matches():
    SUMMARY = "Data comparison completed successfully"
    MESSAGE = f"The data comparison has been completed successfully! There are no differences between the datasets."
    markdown_table = f"{df_edw.to_markdown(index=False)}"
    full_message = MESSAGE + "\n\n" + markdown_table

    # Add a summary to the message
    myTeamsMessage.summary(SUMMARY)

    # Add text to the message
    myTeamsMessage.text(full_message)

    # Log the message
    log.info(
        "Data comparison completed successfully! Message sent to Microsoft Teams."
    )
    log.debug(f"Microsoft Teams summary: {repr(SUMMARY)}")
    log.debug(f"Microsoft Teams message: {repr(MESSAGE)}")
else:
    # Build the message
    SUMMARY = "Data comparison completed with differences"
    MESSAGE = "The data comparison has been completed, but there are differences between the datasets. See the comparison result below:"
    edw_table_markdown = df_edw.to_markdown(index=False)
    pbi_table_markdown = df_pbi.to_markdown(index=False)
    comparison_result = result.to_markdown(index=False)
    full_message = f"{MESSAGE}\n\nEDW dataset:\n\n{edw_table_markdown}\n\nPowerBI dataset:\n\n{pbi_table_markdown}\n\nComparison result:\n\n{comparison_result}"

    # Add a summary to the message
    myTeamsMessage.summary(SUMMARY)

    # Add text to the message
    myTeamsMessage.text(full_message)

    # Log the message
    log.warning(
        "Data comparison completed with differences! Message sent to Microsoft Teams."
    )
    log.debug(f"Microsoft Teams summary: {repr(SUMMARY)}")
    log.debug(f"Microsoft Teams message: {repr(MESSAGE)}")

# Send message
myTeamsMessage.send()

# Print to console
log.info("The process has been completed!")

# Close connections
conn_EDW.close()
conn_BI.close()

log.debug(f"Ending the process {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
