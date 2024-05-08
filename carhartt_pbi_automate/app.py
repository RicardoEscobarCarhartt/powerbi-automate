##################################################################### Libraries ####################################################################################
import os
import time
from datetime import datetime
import threading

import pyautogui
import pandas as pd
import datacompy
import pymsteams
from dotenv import load_dotenv

from connector import get_edw_connection, get_bi_connection
from popup import detect_popup_window


# Load environment variables from .env file
load_dotenv()


# Define a variable to store the connection to Power BI
conn_BI_result = [None]

# Define a function that wraps get_bi_connection
def get_connection():
    conn_BI = get_bi_connection(
        "powerbi://api.powerbi.com/v1.0/myorg/BI-Datasets", "Supply"
    )
    # Save the result in the list
    conn_BI_result[0] = conn_BI

def get_edw_start_end_dates(edw_data_frame):
    """
    Get the start and end dates from the EDW data frame
    """
    start_date = edw_data_frame["YearPeriodMonth"].min()
    end_date = edw_data_frame["YearPeriodMonth"].max()
    # Start date: "2024-P07-Jan" convert into "2024-07", End date: "2025-P06-Dec" convert into "2025-06"
    start_date = (
        '"'
        + start_date.split("-P")[0]
        + "-"
        + start_date.split("-P")[1][:2]
        + '"'
    )
    end_date = (
        '"' + end_date.split("-P")[0] + "-" + end_date.split("-P")[1][:2] + '"'
    )
    return start_date, end_date


##################################################################### Connections ##################################################################################
#################### EDW CONNECTION ####################
print("Connecting to EDW...")
while True:
    try:
        conn_EDW = get_edw_connection("DBNSQLPNET")
        print("Connection to EDW has been established!")
        break
    except Exception as error:
        print(f"Error: {error}")
        print("Trying to connect again...")
        continue

#################### POWER BI CONNECTION ####################
is_powerbi_logged_in = False
while True:
    try:
        # Create a thread for get_connection
        thread1 = threading.Thread(target=get_connection)

        # Start the thread
        thread1.start()

        # Wait for the pop-up to appear (adjust as needed)
        print("Waiting for the pop-up to appear...")
        time.sleep(2)

        # Check if the pop-up window has been detected
        printed_once = False
        while is_powerbi_logged_in == False:
            try:
                # Check if the connection has been established
                if conn_BI_result[0] is not None:
                    break
                # Call detect_popup_window while get_connection is running in the other thread
                detect_popup_window(".*Iniciar sesión en la cuenta.*")
                is_powerbi_logged_in = True
            except Exception as error:
                time.sleep(2)
                if printed_once:
                    break
                else:
                    print(f"Error: {error}")
                    print("Click the 'Sign In' button manually.")
                    printed_once = True

        # Wait for the thread to finish
        thread1.join()

        # Get the connection from the list
        conn_BI = conn_BI_result[0]
        break
    except Exception as error:
        print(f"Error: {error}")
        try_again = input("Do you want to try again? (y/n): ")
        if try_again.lower() != "y":
            print("Exiting the program...")
            exit()
        continue

print("Connection to Power BI has been established!")

#################### TEAMS CONNECTOR ####################
teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)
print("Connection to Teams has been established!")

##################################################################### Coding (Data Extraction) #######################################################################################
#################### (1) DATASET EDW SQL SERVER ####################
query_edw = """
DECLARE @VersionDateToValidate INT;
SET @VersionDateToValidate =
(
    SELECT [DateKey]
    FROM [CarharttDw].[Dimensions].[Days]
    WHERE [CurrentDayOffset] = 0
);
 
----Sales Demand Units = SalesForecastUnits in EDW---
SELECT TRIM([DT].[YearPeriodMonth]) 'YearPeriodMonth',
       SUM([SCP].[SalesForecastUnits]) 'SalesDemandUnits',
       SUM([SCP].[CurrentTotalReceiptPlanUnits]) 'TotalReceiptPlanUnits',
       SUM([SCP].[PlannedProductionUnits]) 'PlannedProductionUnits'
FROM [CarharttDw].[planning].[SizedWeeklyCombinedPlans] SCP
    INNER JOIN [CarharttDw].[Dimensions].[Days] DT
        ON [DT].[DateKey] = [SCP].[FiscalWeekDateKey]
    INNER JOIN [CarharttDw].[Dimensions].[Products] P
        ON [P].[ProductKey] = [SCP].[ProductKey]
WHERE [SCP].[PlanType] = 'NIGHTLY'
      AND [SCP].[VersionDateKey] = @VersionDateToValidate --Is Key for SavedPlanName
      AND [DT].[CurrentYearOffset] IN ( 0, 1 )
      AND [DT].[CurrentSeasonOffset] IN ( 0, 1 )
      AND [SCP].[InventorySegment] <> 'ALL' --Visible
      AND [P].[Licensed] <> 'Y' --Visible 
      AND [P].[Licensed] IS NOT NULL --Hidden
GROUP BY [DT].[YearPeriodMonth]
ORDER BY [DT].[YearPeriodMonth];
"""
time_start = datetime.now()
print("Extracting data from EDW...")
df_edw = pd.read_sql(query_edw, conn_EDW)
time_end = datetime.now()
time_diff = time_end - time_start
# print(f"Time to extract data from EDW: {time_diff}")
print(
    f"Time to extract data from EDW: {time_diff.seconds // 3600} hours {(time_diff.seconds // 60) % 60} minutes {time_diff.seconds % 60} seconds"
)
print("Data from EDW has been extracted!")

#################### (2) DATASET BI DASHBOARD ####################
cursor_data_BI = conn_BI.cursor()
inventory_plans_start_month, inventory_plans_end_month = (
    get_edw_start_end_dates(df_edw)
)
print(f"Start month: {inventory_plans_start_month}")
print(f"End month: {inventory_plans_end_month}")
now = datetime.now()
nightly_current_date = f'"NIGHTLY-{now.month}/{now.day}/{now.year}"'
query_dax = f"""
// DAX Query
DEFINE
    MEASURE '#Local Measures'[SlicerCheck] = 
        (/* USER DAX BEGIN */

CALCULATE ( IF ( ISFILTERED ( 'Plan Versions'[Plan Name] ), 1, 0 ), ALLSELECTED ( 'Plan Versions' ) )
/* USER DAX END */)

    VAR __DS0FilterTable = 
        TREATAS({{{inventory_plans_start_month}}}, 'Inventory Plans Start Month'[Start Fiscal Year/Month])

    VAR __DS0FilterTable2 = 
        TREATAS({{{inventory_plans_end_month}}}, 'Inventory Plans End Month'[End Fiscal Year/Month])

    VAR __DS0FilterTable3 = 
        TREATAS({{"NIGHTLY"}}, 'Plan Versions'[Plan Version])

    VAR __DS0FilterTable4 =
        TREATAS({{{nightly_current_date}}}, 'Plan Versions'[Plan Name])

    VAR __DS0FilterTable5 = 
        FILTER(
            KEEPFILTERS(VALUES('Products'[Is Licensed])),
            AND('Products'[Is Licensed] IN {{"N"}}, NOT('Products'[Is Licensed] IN {{BLANK()}}))
        )

    VAR __DS0FilterTable6 = 
        TREATAS({{"Inv Dem"}}, 'Reporting Notification Messages'[Content ID])

    VAR __ValueFilterDM0 = 
        FILTER(
            KEEPFILTERS(
                SUMMARIZECOLUMNS(
                    'Dates'[Year/Period/Month],
                    'Dates'[Current Month Offset],
                    __DS0FilterTable,
                    __DS0FilterTable2,
                    __DS0FilterTable3,
                    __DS0FilterTable4,
                    __DS0FilterTable5,
                    __DS0FilterTable6,
                    "Sales_Demand_Units", 'Inventory Plans'[Sales Demand Units],
                    "Constrained_Receipt_Plan_Units", 'Inventory Plans'[Constrained Receipt Plan Units],
                    "Total_Receipt_Plan_Units", 'Inventory Plans'[Total Receipt Plan Units],
                    "Forward_Weeks_Of_Coverage", 'Inventory Plans'[Forward Weeks Of Coverage],
                    "Planned_Production_Units", 'Inventory Plans'[Planned Production Units],
                    "Work_In_Progress_Units", 'Inventory Plans'[Work In Progress Units],
                    "In_Transit_Units", 'Inventory Plans'[In Transit Units],
                    "SlicerCheck", IGNORE('#Local Measures'[SlicerCheck])
                )
            ),
            [SlicerCheck] = 1
        )

    VAR __DS0Core = 
        SUMMARIZECOLUMNS(
            'Dates'[Year/Period/Month],
            'Dates'[Current Month Offset],
            __DS0FilterTable,
            __DS0FilterTable2,
            __DS0FilterTable3,
            __DS0FilterTable4,
            __DS0FilterTable5,
            __DS0FilterTable6,
            __ValueFilterDM0,
            "SalesDemandUnits", 'Inventory Plans'[Sales Demand Units],
            "ConstrainedReceiptPlanUnits", 'Inventory Plans'[Constrained Receipt Plan Units],
            "TotalReceiptPlanUnits", 'Inventory Plans'[Total Receipt Plan Units],
            "ForwardWeeksOfCoverage", 'Inventory Plans'[Forward Weeks Of Coverage],
            "PlannedProductionUnits", 'Inventory Plans'[Planned Production Units],
            "WorkInProgressUnits", 'Inventory Plans'[Work In Progress Units],
            "InTransitUnits", 'Inventory Plans'[In Transit Units]
        )

    VAR __DS0PrimaryWindowed = 
        TOPN(501, __DS0Core, 'Dates'[Current Month Offset], 1, 'Dates'[Year/Period/Month], 1)

EVALUATE
    __DS0PrimaryWindowed

ORDER BY
    'Dates'[Current Month Offset], 'Dates'[Year/Period/Month]

"""
print("Extracting data from Power BI...")
time_start = datetime.now()
cursor_data_BI.execute(query_dax)
results_table = cursor_data_BI.fetchall()
column_names = [
    column[0].replace("[", "").replace("]", "")
    for column in cursor_data_BI.description
]
data_table = list(results_table)
df_bi = pd.DataFrame(data_table, columns=column_names)
cursor_data_BI.close()
time_end = datetime.now()
time_diff = time_end - time_start
print(
    f"Time to extract data from Power BI: {time_diff.seconds // 3600} hours {(time_diff.seconds // 60) % 60} minutes {time_diff.seconds % 60} seconds"
)
print("Data from Power BI has been extracted!")

# Modify the column name to match the EDW dataset
df_bi.rename(
    columns={
        "DatesYear/Period/Month": "YearPeriodMonth",
    },
    inplace=True,
)

# Drop the columns that are not in the EDW dataset
df_bi.drop(
    columns=[
        "DatesCurrent Month Offset",
        "ConstrainedReceiptPlanUnits",
        "ForwardWeeksOfCoverage",
        "WorkInProgressUnits",
        "InTransitUnits",
    ],
    inplace=True,
)

# Apply ORDER BY YearPeriodMonth on both dataframes
df_bi = df_bi.sort_values(by="YearPeriodMonth").reset_index(drop=True)
df_edw = df_edw.sort_values(by="YearPeriodMonth").reset_index(drop=True)

# Save the dataframes to csv files
df_edw.to_csv("edw_data.csv", index=False)
df_bi.to_csv("bi_data.csv", index=False)

# Use the datacompy library to compare the dataframes
compare = datacompy.Compare(df_bi, df_edw, on_index=True)
compare.matches(ignore_extra_columns=False)
result = compare.all_mismatch()
result_html = result.to_html(index=False)

# Generate a timestamp to use in the result file name
timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Create results/ folder if it does not exist
if not os.path.exists("results"):
    os.makedirs("results")
result_file = os.path.join("results", f"{timestamp}_comparison_result.html")

# Save the comparison result to a file
with open(result_file, "w", encoding="utf-8") as file:
    file.write(result_html)

# Create the connectorcard object
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)

# If the comparation its ok do nothing, if not send a notification to the channel in teams
if compare.matches():
    # Add a summary to the message
    myTeamsMessage.summary("Data comparison completed successfully")

    # Add text to the message
    myTeamsMessage.text(
        f"The data comparison has been completed successfully! There are no differences between the datasets."
        f"\n\n{df_edw.to_markdown(index=False)}"
    )
else:
    # Add a summary to the message
    myTeamsMessage.summary("Data comparison completed with differences")

    # Add text to the message
    myTeamsMessage.text(
        "The data comparison has been completed, but there are differences between the datasets. See the comparison result below:\n\n"
        f"Compare result:\n\n{result.to_markdown(index=False)}\n"
        f"EDW dataset:\n\n{df_edw.to_markdown(index=False)}\n"
        f"PowerBI dataset:\n\n{df_bi.to_markdown(index=False)}"
    )

# Send message
myTeamsMessage.send()

# Close connections
conn_EDW.close()
conn_BI.close()
exit()

#################### (3) DATASET BI DASHBOARD ####################


###################################################################### Coding (Testing and Monitoring) #####################################################################################
# --------------------------------------------------------------------------------------------------------------------------------------------------------------#
# (1) REVIEWING IF THE DASHBOARD IT IS UP TO DATE
# if the dashboard refreshed date is lowest than current day
if date_formated_object < current_date_object:
    # Send a notification to the channel in teams
    Section1 = pymsteams.cardsection()
    # Title
    Section1.title(
        "-------------------------------------------------------------------------------------------"
    )
    # Message
    Section1.activityTitle(
        "<p>&#128270;<FONT SIZE=4.5><b> 1st Review: Is the dashboard updated?</b></FONT></p>"
    )
    Section1.activitySubtitle('<B><FONT COLOR="red"> Failed!</FONT>')
    Section1.text(
        "-------------------------------------------------------------------------------------------"
    )
    myTeamsMessage.addSection(Section1)
else:
    # if the dashboard refreshed date is the current
    # Send a notification to the channel in teams
    Section1 = pymsteams.cardsection()
    # Title
    Section1.title(
        "-------------------------------------------------------------------------------------------"
    )
    # Message
    Section1.activityTitle(
        "<p>&#128270;<FONT SIZE=4.5><b> 1st Review: Is the dashboard updated?</b></FONT></p>"
    )
    Section1.activitySubtitle('<B><FONT COLOR="green"> Passed!</FONT>')
    Section1.text(
        "-------------------------------------------------------------------------------------------"
    )
    myTeamsMessage.addSection(Section1)

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # (2) REVIEWING IF THE DATASET FROM POWER BI MATCH WITH THE DATASET FROM EDW
    compare = datacompy.Compare(df_bi, df_edw, on_index=True)
    compare.matches(ignore_extra_columns=False)
    result = compare.all_mismatch()
    result_html = result.to_html(index=False)
    # If the comparation its ok
    if compare.matches() == True:
        # Notification to channel in teams
        Section2 = pymsteams.cardsection()
        # Title
        Section2.title(
            "<p>&#128270;<FONT SIZE=4.5><b> 2nd Review: Its the Power BI Dataset the same as the EWD Dataset?</b></FONT></p>"
        )
        # Message
        Section2.activitySubtitle('<B><FONT COLOR="green"> Passed!')
        Section2.text(
            "-------------------------------------------------------------------------------------------"
        )
        myTeamsMessage.addSection(Section2)
    else:
        # Notification to channel in teams
        Section2 = pymsteams.cardsection()
        # Title
        Section2.title(
            "<p>&#128270;<FONT SIZE=4.5><b> 2nd Review: Its the Power BI Dataset the same as the EWD Dataset?</b></FONT></p>"
        )
        # Message
        Section2.activitySubtitle(
            f'<B><FONT COLOR="red"> Failed!, see next table:\n {result_html}'
        )
        Section2.text(
            "-------------------------------------------------------------------------------------------"
        )
        myTeamsMessage.addSection(Section2)

# Send message
myTeamsMessage.text(
    f'<B><FONT SIZE=4 COLOR="cyan"> Today´s reviews for {current_date_formated} have been completed!. See more:'
)
myTeamsMessage.addLinkButton(
    "Go to the Dashboard",
    "https://app.powerbi.com/groups/1045beda-05ae-4d05-b359-324d1bf5b8e6/reports/f04bd57d-09c5-4ecf-b15b-6680f5e1cb65/ReportSection2f97a10d13ae57614624?ctid=b4e848aa-20ef-4814-a34a-93fe53f3970f&experience=power-bi",
)
myTeamsMessage.send()
# Print to console
print("The process has been completed!")
