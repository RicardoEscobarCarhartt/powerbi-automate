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
conn_EDW = get_edw_connection("DBNSQLPNET")
print("Connection to EDW has been established!")

#################### POWER BI CONNECTION ####################
conn_BI = get_bi_connection("powerbi://api.powerbi.com/v1.0/myorg/BI-Datasets", "Supply")
print("Connection to Power BI has been established!")

#################### TEAMS CONNECTOR ####################
teams_webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)
exit()

##################################################################### Coding (Data Extraction) #######################################################################################
#################### (1) DATASET EDW SQL SERVER ####################
query_edw = """
SELECT 
      TotalTables AS Total_Tables
	  ,TotalStoredProcedures AS Stored_Procedures
      ,TotalViews AS Total_Views
	  ,TotalTriggers AS Total_Triggers
	  ,TotalSSISpackage AS Total_SSIS_packages
  FROM [CarharttDw].[Utility].[DataflowUsedSpaceLogView]
  WHERE CAST([DateInsert] AS date) = CAST(GETDATE() AS DATE)
"""
df_edw = pd.read_sql(query_edw, conn_EDW)

#################### (2) DATASET BI DASHBOARD ####################
cursor_data_BI = conn_BI.cursor()
query_dax = """
DEFINE 
    VAR __DS0FilterTable = 
	    TREATAS({"Y"}, 'Is Last Date'[Is Last Date])

EVALUATE
    SUMMARIZECOLUMNS(
        __DS0FilterTable, 
        "Total_Tables", IGNORE('Database Details'[Total Tables]),
        "Stored_Procedures", IGNORE('Database Details'[Stored Procedures]),
        "Total_Views", IGNORE('Database Details'[Total Views]),
        "Total_Triggers", IGNORE('Database Details'[Total Triggers]),
        "Total_SSIS_packages", IGNORE('Database Details'[Total SSIS packages])
		)
    """
cursor_data_BI.execute(query_dax)
results_table = cursor_data_BI.fetchall()
column_names = [column[0].replace('[', '').replace(']', '') for column in cursor_data_BI.description]
data_table = list(results_table)
df_bi = pd.DataFrame(data_table, columns=column_names)
cursor_data_BI.close()

#################### (3) REFRESHED DATE BI DASHBOARD ####################
cursor_refresh_BI = conn_BI.cursor()
query_dax_refresh = """
DEFINE VAR __DS0FilterTable = 
	TREATAS({"Y"}, 'Is Last Date'[Is Last Date])

EVALUATE
	SUMMARIZECOLUMNS(__DS0FilterTable, "Last_refresh", IGNORE('Database Details'[Last refresh]))
"""
cursor_refresh_BI.execute(query_dax_refresh)
results_refresh = cursor_refresh_BI.fetchall()
data_refresh = list(results_refresh)
df_refresh_bi = pd.DataFrame(data_refresh)
cursor_refresh_BI.close()


##################################################################### Coding (Data Cleansing) #######################################################################################
#################### (1) Dataframe EDW SQL SERVER #######################


#################### (2) REFRESHED DATE BI DASHBOARD ####################
# FORMATING LAST UPDATE VALUE
date_value = df_refresh_bi.iloc[0, 0]
date_value_new = date_value.replace("Current as of ", "")
# Fixing format to DD/MM/YYYY
date_object = datetime.strptime(date_value_new, "%b %d, %Y")
date_formated = date_object.strftime("%d/%m/%Y")
date_formated_object = datetime.strptime(date_formated,"%d/%m/%Y")
# Extracting current date
current_date = datetime.now()
current_date_formated = current_date.strftime("%d/%m/%Y")
current_date_object = datetime.strptime(current_date_formated,"%d/%m/%Y")

#################### (3) DATASET BI DASHBOARD ####################


###################################################################### Coding (Testing and Monitoring) #####################################################################################
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# (1) REVIEWING IF THE DASHBOARD IT IS UP TO DATE
# if the dashboard refreshed date is lowest than current day
if date_formated_object < current_date_object:
	# Send a notification to the channel in teams
	Section1 = pymsteams.cardsection()
	# Title
	Section1.title("-------------------------------------------------------------------------------------------")
	# Message
	Section1.activityTitle('<p>&#128270;<FONT SIZE=4.5><b> 1st Review: Is the dashboard updated?</b></FONT></p>')
	Section1.activitySubtitle('<B><FONT COLOR="red"> Failed!</FONT>')
	Section1.text("-------------------------------------------------------------------------------------------")
	myTeamsMessage.addSection(Section1)
else:
    # if the dashboard refreshed date is the current
	# Send a notification to the channel in teams
	Section1 = pymsteams.cardsection()
	# Title
	Section1.title("-------------------------------------------------------------------------------------------")
	# Message
	Section1.activityTitle('<p>&#128270;<FONT SIZE=4.5><b> 1st Review: Is the dashboard updated?</b></FONT></p>')
	Section1.activitySubtitle('<B><FONT COLOR="green"> Passed!</FONT>')
	Section1.text("-------------------------------------------------------------------------------------------")
	myTeamsMessage.addSection(Section1)
	
#--------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # (2) REVIEWING IF THE DATASET FROM POWER BI MATCH WITH THE DATASET FROM EDW
	compare = datacompy.Compare(df_bi, df_edw, on_index=True)
	compare.matches(ignore_extra_columns= False)
	result = compare.all_mismatch()
	result_html = result.to_html(index=False)
    # If the comparation its ok
	if compare.matches() == True :
		# Notification to channel in teams
		Section2 = pymsteams.cardsection()
		# Title
		Section2.title('<p>&#128270;<FONT SIZE=4.5><b> 2nd Review: Its the Power BI Dataset the same as the EWD Dataset?</b></FONT></p>')
		# Message
		Section2.activitySubtitle('<B><FONT COLOR="green"> Passed!')
		Section2.text("-------------------------------------------------------------------------------------------")
		myTeamsMessage.addSection(Section2)
	else:
		# Notification to channel in teams
		Section2 = pymsteams.cardsection()
		# Title
		Section2.title('<p>&#128270;<FONT SIZE=4.5><b> 2nd Review: Its the Power BI Dataset the same as the EWD Dataset?</b></FONT></p>')
		# Message
		Section2.activitySubtitle(f'<B><FONT COLOR="red"> Failed!, see next table:\n {result_html}')
		Section2.text("-------------------------------------------------------------------------------------------")
		myTeamsMessage.addSection(Section2)

# Send message
myTeamsMessage.text(f'<B><FONT SIZE=4 COLOR="cyan"> Today´s reviews for {current_date_formated} have been completed!. See more:')
myTeamsMessage.addLinkButton('Go to the Dashboard','https://app.powerbi.com/groups/1045beda-05ae-4d05-b359-324d1bf5b8e6/reports/f04bd57d-09c5-4ecf-b15b-6680f5e1cb65/ReportSection2f97a10d13ae57614624?ctid=b4e848aa-20ef-4814-a34a-93fe53f3970f&experience=power-bi')
myTeamsMessage.send()
# Print to console
print("The process has been completed!")