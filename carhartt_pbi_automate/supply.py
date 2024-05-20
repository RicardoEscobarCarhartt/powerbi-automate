"""this module contains functions to automate the supply data comparison
process"""

import pandas as pd


def get_edw_start_end_dates(edw_data_frame: pd.DataFrame) -> tuple[str, str]:
    """
    Get the start and end dates from the EDW data frame.
    This function only works with the `sql\\supply.sql` query and is not meant
    to be used with any other SQL query.
    Args:
        edw_data_frame (pd.DataFrame): The data frame from the EDW.
    Returns:
        Tuple[str, str]: A tuple containing the start and end dates.
    Examples:
        Start date: "2024-P07-Jan" convert into "2024-07"
        And End date: "2025-P06-Dec" convert into "2025-06"
    """
    start_date: str = edw_data_frame["YearPeriodMonth"].min()
    end_date: str = edw_data_frame["YearPeriodMonth"].max()

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


def get_dax_query(
    inventory_plans_start_month: str,
    inventory_plans_end_month: str,
    nightly_current_date: str,
) -> str:
    """
    Get the DAX query for the supply data comparison.
    Args:
        inventory_plans_start_month (str): The inventory plans start month.
        inventory_plans_end_month (str): The inventory plans end month.
        nightly_current_date (str): The nightly current date.
    Returns:
        str: The DAX query.
    """
    dax_query = f"""
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
    return dax_query


def trim_dax_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    This function removes unnecessary columns from the Power BI dataset.
    And renames the YearPeriodMonth column to match the EDW dataset.
    Args:
        dataframe (pd.DataFrame): The Power BI dataset.
    Returns:
        pd.DataFrame: The cleaned Power BI dataset.
    """
    # Modify the column name to match the EDW dataset
    dataframe.rename(
        columns={
            "DatesYear/Period/Month": "YearPeriodMonth",
        },
        inplace=True,
    )

    # Drop the columns that are not in the EDW dataset
    dataframe.drop(
        columns=[
            "DatesCurrent Month Offset",
            "ConstrainedReceiptPlanUnits",
            "ForwardWeeksOfCoverage",
            "WorkInProgressUnits",
            "InTransitUnits",
        ],
        inplace=True,
    )
    return dataframe
