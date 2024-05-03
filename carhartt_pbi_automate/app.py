##################################################################### Libraries ####################################################################################
import os
from datetime import datetime

import pandas as pd
import datacompy
import pymsteams
from dotenv import load_dotenv

from connector import get_edw_connection, get_bi_connection


# Load environment variables from .env file
load_dotenv()

##################################################################### Connections ##################################################################################
#################### EDW CONNECTION ####################
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
conn_BI = get_bi_connection(
    "powerbi://api.powerbi.com/v1.0/myorg/BI-Datasets", "Supply"
)
print("Connection to Power BI has been established!")

#################### TEAMS CONNECTOR ####################
teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)
print("Connection to Teams has been established!")

##################################################################### Coding (Data Extraction) #######################################################################################
#################### (1) DATASET EDW SQL SERVER ####################
query_edw = """
-- This query is to be compared to: 'Conectado a Supply.xlsx'
SELECT [DT].[ActualDate] as [Version Date],
       TRIM([EVT].[YearPeriodMonth]) as [YearPeriodMonth],
       SUM(SCP.SalesForecastUnits) 'SalesDemandUnits',
       SUM(SCP.CurrentTotalReceiptPlanUnits) 'TotalReceiptPlanUnits',
       SUM(SCP.PlannedProductionUnits) 'PlannedProductionUnits',
       SUM([SCP].[HighSurplusUnits]) [HighSurplusUnits],
       SUM([SCP].[LowSurplusUnits]) [LowSurplusUnits],
       SUM([SCP].[InventoryTargetRiskUnits] - [SCP].[HighRiskUnits]) AS 'LowRisk',
	   ---Max Date of Period
	   SUM([SCP].[HighRiskUnits]) AS 'HighRisk',
       SUM([SCP].[InventoryTargetRiskUnits]) 'Inventory Target Risk Units',
       SUM([SCP].[InventoryTargetSurplusUnits]) 'Inventory Target Surplus Units'
FROM [CarharttDw].[Planning].[SizedWeeklyCombinedPlans] SCP
    INNER JOIN [Dimensions].[Days] DT
        ON [SCP].[VersionDateKey] = [DT].[DateKey]
    INNER JOIN [Dimensions].[Days] EVT
        ON [EVT].[DateKey] = [SCP].[FiscalWeekDateKey]
    INNER JOIN [Dimensions].[Products] P
        ON [P].[ProductKey] = [SCP].[ProductKey]
WHERE
    --View Filters
    [SCP].[PlanType] = 'NIGHTLY'
    AND [SCP].[InventorySegment] != 'ALL'
    AND [SCP].[ExtendedEOP] = 'N'
    --PBI Filters Hidden
    and [P].[Department] in ( 'Men''s', 'Women''s', 'Personal Protective' ) --Hidden
    AND EVT.YearPeriodMonth IS NOT NULL
    AND [EVT].[CurrentYearOffset] IN ( 0,1)
    and [EVT].[CurrentSeasonOffset] IN (0,1)
    and [P].[StockCategory] = 'A'
    and [P].[SalesStatus] <> 'Z1'
    and P.StillInERP = 'Y' --FirstQuality
    --PBI Visible Filters
    AND [SCP].[VersionDateKey] =
    (
        SELECT [DateKey] FROM [Dimensions].[Days] WHERE [CurrentDayOffset] = 0
    )    
GROUP BY [DT].[ActualDate],
         [EVT].[YearPeriodMonth]
ORDER BY [EVT].[YearPeriodMonth];
"""
time_start = datetime.now()
print("Extracting data from EDW...")
df_edw = pd.read_sql(query_edw, conn_EDW)
time_end = datetime.now()
print(f"Time to extract data from EDW: {time_end - time_start}")
print("Data from EDW has been extracted!")

#################### (2) DATASET BI DASHBOARD ####################
cursor_data_BI = conn_BI.cursor()
inventory_plans_start_month = '"2024-09"'
inventory_plans_end_month = '"2025-09"'
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
print(f"Time to extract data from Power BI: {time_end - time_start}")
print("Data from Power BI has been extracted!")

# Save the dataframes to csv files
df_edw.to_csv("edw_data.csv", index=False)
df_bi.to_csv("bi_data.csv", index=False)

# Close connections
conn_EDW.close()
conn_BI.close()
exit()

#################### (3) REFRESHED DATE BI DASHBOARD ####################
# cursor_refresh_BI = conn_BI.cursor()
# query_dax_refresh = """
# DEFINE VAR __DS0FilterTable = 
#     TREATAS({"Y"}, 'Is Last Date'[Is Last Date])

# EVALUATE
#     SUMMARIZECOLUMNS(__DS0FilterTable, "Last_refresh", IGNORE('Database Details'[Last refresh]))
# """
# cursor_refresh_BI.execute(query_dax_refresh)
# results_refresh = cursor_refresh_BI.fetchall()
# data_refresh = list(results_refresh)
# df_refresh_bi = pd.DataFrame(data_refresh)
# cursor_refresh_BI.close()


##################################################################### Coding (Data Cleansing) #######################################################################################
#################### (1) Dataframe EDW SQL SERVER #######################


#################### (2) REFRESHED DATE BI DASHBOARD ####################
# FORMATING LAST UPDATE VALUE
date_value = df_refresh_bi.iloc[0, 0]
date_value_new = date_value.replace("Current as of ", "")
# Fixing format to DD/MM/YYYY
date_object = datetime.strptime(date_value_new, "%b %d, %Y")
date_formated = date_object.strftime("%d/%m/%Y")
date_formated_object = datetime.strptime(date_formated, "%d/%m/%Y")
# Extracting current date
current_date = datetime.now()
current_date_formated = current_date.strftime("%d/%m/%Y")
current_date_object = datetime.strptime(current_date_formated, "%d/%m/%Y")

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
