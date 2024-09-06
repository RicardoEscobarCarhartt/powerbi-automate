"""This module contains the main code for the Carhartt Power BI Automation
project. This script extracts data from the EDW and Power BI databases,
compares the supply data"""

import os
import sys
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
from get_logger import get_logger
from dax import pass_args_to_dax_query
from parse_arguments import parse_arguments
from get_formated_duration import get_formated_duration
from send_teams_message import send_ok_teams_message, send_fail_teams_message


# Constants
# The path to the directory where the script is located
SCRIPT_DIR = Path(__file__).resolve().parent

# The path to project root directory
ROOT_DIR = SCRIPT_DIR.parent

# The path to the directory where the logs are stored
LOGS_DIR = ROOT_DIR / "logs"

# Log name
LOG_NAME = "run_supply"

# Log file path
LOG_FILE = (LOGS_DIR / LOG_NAME).with_suffix(".log")


# The path to the directory where the results are stored
RESULTS_DIR = ROOT_DIR / "results"

# The path to the directory where the DAX and SQL files are stored
QUERIES_DIR = ROOT_DIR / "queries"

# Create a logger object
log = get_logger(LOG_NAME, LOG_FILE)

# Arguments for EDW and Power BI connections
EDW_ARGS = {
    "server": "DBNSQLPNET",
    "database": "CarharttDw",
    "driver": "ODBC Driver 17 for SQL Server",
}

PBI_ARGS = {
    "server": "powerbi://api.powerbi.com/v1.0/myorg/BI-Datasets",
    "database": "Supply",
}

# Detect the pop-up window titles
POPUP_WINDOW_TITLES = [
    ".*Sign in to your account.*",
    ".*Iniciar sesión en la cuenta.*",
]

# Load environment variables from .env file
load_dotenv()

# Define a global variable to store the connection to Power BI
# To be accessed from a thread.
conn_BI_result: List[adodbapi.Connection] = [None]

# Parse script arguments
try:
    script_args = parse_arguments()
    log.debug("Script arguments: %s", script_args)
    log.debug("DAX file path: %s", script_args.daxfile)
    log.debug("SQL file path: %s", script_args.sqlfile)
except argparse.ArgumentError as error:
    STACK_TRACE = traceback.format_exc()
    log.error("Error: %s", error)
    log.error("Stack trace: %s", STACK_TRACE)
    log.critical("Failed to parse script arguments. Exiting the program.")
    sys.exit(1)


# Define a function that wraps get_bi_connection.
def get_connection(
    server: str = "powerbi://api.powerbi.com/v1.0/myorg/BI-Datasets",
    database: str = "Supply",
):
    """
    Get the connection to Power BI. This function is called from a Thread.
    That's why the connection is saved in a list to be accessed, rather than
    returned.
    """
    # Save the result in the list
    conn_BI_result[0] = get_bi_connection(server, database)


script_start_time = datetime.now()
log.debug(
    "Starting the process %s", script_start_time.strftime("%Y-%m-%d %H:%M:%S")
)

# Connect to the EDW database.
log.info("Connecting to EDW...")
while True:
    try:
        conn_EDW = get_edw_connection(EDW_ARGS)
        log.info("Connection to EDW has been established!")
        break
    except Exception as error:  # pylint: disable=broad-except
        STACK_TRACE = traceback.format_exc()
        log.error("Error: %s", error)
        log.error("Stack trace: %s", STACK_TRACE)
        log.info("Trying to connect again...")
        continue

# Connect to Power BI database.
IS_POWERBI_LOGGED_IN = False
RETRY_COUNT = 3
while True:
    try:
        # Create a thread for get_connection
        thread1 = threading.Thread(target=get_connection, kwargs=PBI_ARGS)

        # Start the thread
        thread1.start()

        # Wait for the pop-up to appear (adjust as needed)
        log.info("Waiting for the pop-up to appear...")
        time.sleep(4)

        # Check if the pop-up window has been detected
        printed_once = False  # pylint: disable=invalid-name
        while not IS_POWERBI_LOGGED_IN:
            try:
                # Check if the connection has been established
                if conn_BI_result[0] is not None:
                    break
                # Call detect_popup_window while get_connection is running in the other thread
                detect_popup_window(POPUP_WINDOW_TITLES)
                IS_POWERBI_LOGGED_IN = True
            except Exception as error:  # pylint: disable=broad-except
                time.sleep(2)
                if printed_once:
                    break
                else:
                    STACK_TRACE = traceback.format_exc()
                    log.error("Error: %s", error)
                    log.error("Stack trace: %s", STACK_TRACE)
                    log.info("Trying to log in again...")
                    printed_once = True

        # Wait for the thread to finish
        thread1.join()

        # Get the connection from the list
        conn_bi = conn_BI_result[0]  # pylint: disable=invalid-name
        break
    except (pymsteams.TeamsWebhookException, adodbapi.DatabaseError) as error:
        STACK_TRACE = traceback.format_exc()
        log.error("Error: %s", error)
        log.error("Stack trace: %s", STACK_TRACE)
        if RETRY_COUNT:
            log.info("Trying to connect again...")
            RETRY_COUNT -= 1
            continue
        else:
            STACK_TRACE = traceback.format_exc()
            log.critical(
                "Failed to connect. Exiting the program. Please check the logs for more information."
            )
            log.critical("Stack trace: %s", STACK_TRACE)
            sys.exit(1)

log.info("Connection to Power BI has been established!")

# Define the webhook URL for Microsoft Teams
teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)
log.info("Connection to Teams has been established!")

# Load supply.sql file and run the query
time_start = datetime.now()
log.info("Extracting data from EDW...")
supply_sql_filepath = Path(script_args.sqlfile)
with open(supply_sql_filepath, "r", encoding="utf-8") as file:
    query_edw = file.read()
    try:
        df_edw = pd.read_sql(query_edw, conn_EDW)
    except (pymsteams.TeamsWebhookException, adodbapi.DatabaseError) as error:
        STACK_TRACE = traceback.format_exc()
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

        log.critical("Data comparison failed: %s", error)
        log.critical("Stack trace: %s", STACK_TRACE)
        sys.exit(1)

end_time = datetime.now()
time_diff = end_time - time_start

# Calculate the time taken to extract data from EDW
formated_duration = get_formated_duration(time_diff)

# Print the time taken to extract data from EDW
log.info("Data from EDW has been extracted.")
log.debug("It took: %s to extract data from EDW.", formated_duration)

# Extract data from Power BI
cursor_data_BI = conn_bi.cursor()

# Load the DAX query from file
dax_query = Path(script_args.daxfile).read_text(encoding="utf-8")

# Pass the arguments to the DAX query
now = datetime.now()
plan_versions = f"NIGHTLY-{now.month}/{now.day}/{now.year}"
log.debug("Plan_versions: %s", plan_versions)
args = {"plan_versions": plan_versions}
dax_query = pass_args_to_dax_query(dax_query, args)

log.info("Extracting data from Power BI...")
time_start = datetime.now()

# Execute the DAX query
try:
    cursor_data_BI.execute(dax_query)
    results_table = cursor_data_BI.fetchall()
except Exception as error:  # pylint: disable=broad-except
    STACK_TRACE = traceback.format_exc()

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

    log.critical("Data comparison failed: %s", error)
    log.critical("Stack trace: %s", STACK_TRACE)
    sys.exit(1)

# Get the column names from the cursor, remove the brackets and create a list
column_names = [
    column[0].replace("[", "").replace("]", "")
    for column in cursor_data_BI.description
]

# Create a dataframe from the results
data_table = list(results_table)
df_pbi = pd.DataFrame(data_table, columns=column_names)
cursor_data_BI.close()
end_time = datetime.now()
time_diff = end_time - time_start

# Calculate the time taken to extract data from Power BI
formated_duration = get_formated_duration(time_diff)
log.info("Data from Power BI has been extracted!")
log.debug("Time to extract data from Power BI: %s", formated_duration)

# Get the first column name from the dataframe
# Assuming the first column is the same in both dataframes
first_column = (
    df_pbi.columns[0] if df_pbi.columns[0] == df_edw.columns[0] else None
)

# If the first column is not the same, leave a log message and exit the program
if first_column:
    log.debug(
        'First column: "%s". This is used to order rows in the final table that goes in the Microsoft Teams message.',  # pylint: disable=line-too-long
        first_column,
    )
else:
    log.critical(
        "The first column in the Power BI dataframe is not the same as in the EDW dataframe."
    )
    log.critical("Exiting the program.")
    sys.exit(1)

# Apply ORDER BY the first column on both dataframes
df_pbi = df_pbi.sort_values(by=first_column).reset_index(drop=True)
df_edw = df_edw.sort_values(by=first_column).reset_index(drop=True)

# Use the datacompy library to compare the dataframes
compare = datacompy.Compare(
    df_pbi,
    df_edw,
    on_index=True,
    df1_name="PowerBI",
    df2_name="EDW",
    cast_column_names_lower=True,
)
compare.matches(ignore_extra_columns=True)
result = compare.all_rows_overlap()

# Generate a timestamp to use in the result file name
timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Create results/timestamp folder if it does not exist
results_path = Path("results") / timestamp
results_path.mkdir(parents=True, exist_ok=True)

# Create the comparison result file
result_file = results_path / "comparison_result.html"

# Save the comparison result to a file
HTML_FILE = str(result_file.resolve())
compare_report = compare.report(html_file=HTML_FILE)
log.debug("Comparison result has been saved to %s", HTML_FILE)

# Save the dataframes to csv files
edw_path = results_path / "edw_data.csv"
bi_path = results_path / "bi_data.csv"
df_edw.to_csv(edw_path, index=False)
log.debug("EDW data has been saved to %s", edw_path.resolve())
df_pbi.to_csv(bi_path, index=False)
log.debug("Power BI data has been saved to %s", bi_path.resolve())

# If the comparation its ok do nothing, if not send a notification to the channel in teams
if compare.matches():
    # Build the message
    SUMMARY = "Data comparison completed successfully"
    MESSAGE = """<p>The data comparison has been completed successfully!</p>
    <p>There are no differences between the datasets.</p>
    <hr>
    """
    SECTION_TITLE = "Current data in EDW and Power BI"

    # this is the title of the notification in teams, to differentiate between
    # the different notifications
    notification_title = "✔ " + Path(script_args.daxfile).stem

    # Create a markdown table from the dataframe, this is the table that will
    # be sent to Teams
    markdown_table = f"{df_edw.to_markdown(index=False)}"

    # Create the args dictionary to pass to the function
    message_args = {
        "teams_webhook_url": teams_webhook_url,
        "color": "00FF00",  # Green color in hex
        "notification_title": notification_title,
        "message": MESSAGE,
        "section_title": SECTION_TITLE,
        "section_text": markdown_table,
    }

    # Run the function to send the message to Teams
    if send_ok_teams_message(message_args):
        # Log the message
        log.info(
            "Data comparison completed successfully! Message sent to Microsoft Teams."
        )
    else:
        log.critical("Failed to send message to Microsoft Teams!")
        log.critical("Please check the logs for more information.")
        sys.exit(1)
else:
    # Build the message when there are differences
    SUMMARY = "Data comparison completed with differences"
    MESSAGE = """<p>The data comparison has been completed,
    but there are differences between the datasets.</p>
    <hr>
    """
    EDW_SECTION_TITLE = "Current data in EDW"
    PBI_SECTION_TITLE = "Current data in Power BI"

    # this is the title of the notification in teams, to differentiate between
    # the different notifications
    notification_title = "❌ " + Path(script_args.daxfile).stem

    # Create a markdown table from the dataframes
    edw_table_markdown = df_edw.to_markdown(index=False)
    pbi_table_markdown = df_pbi.to_markdown(index=False)

    # Create the args dictionary to pass to the function
    message_args = {
        "teams_webhook_url": teams_webhook_url,
        "color": "FF0000",  # Red color in hex
        "notification_title": notification_title,
        "message": MESSAGE,
        "compare_report": compare_report,
    }

    # Run the function to send the message to Teams
    if send_fail_teams_message(message_args):
        # Log the message
        log.info(
            "Data comparison completed successfully! Message sent to Microsoft Teams."
        )
    else:
        log.critical("Failed to send message to Microsoft Teams!")
        log.critical("Please check the logs for more information.")
        sys.exit(1)

    # Log the message
    log.warning(
        "Data comparison completed with differences! Message sent to Microsoft Teams."
    )
    log.debug("Microsoft Teams summary: %s", repr(SUMMARY))
    log.debug("Microsoft Teams message: %s", repr(MESSAGE))


# Print to console
log.info("The process has been completed!")

# Close connections
conn_EDW.close()
conn_bi.close()

script_end_time = datetime.now()
script_duration = get_formated_duration(script_end_time - script_start_time)
log.debug(
    "Ending the process at: %s Duration: %s",
    end_time.strftime("%Y-%m-%d %H:%M:%S"),
    script_duration,
)
