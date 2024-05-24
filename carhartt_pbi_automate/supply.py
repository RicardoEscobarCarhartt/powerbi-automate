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
    # if the data frame is empty, raise an error
    if edw_data_frame.empty:
        raise ValueError("The EDW data frame is empty.")

    # get the minimum and maximum dates from the data frame
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
