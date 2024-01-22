"""This module tests the pandas library being used to load the excel file and
test the data."""
from pathlib import Path
import pandas as pd


def test_pandas():
    """Test pandas"""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    print(df.shape)
    assert df.shape == (2, 3)
    print(df)


def load_excel_supply_dataframe(filename: str | Path = None):
    """Test load excel

    Args:
        filename (str | Path, optional): The path to the Excel file. Defaults to None.

    Raises:
        ValueError: If filename is None.
        ValueError: If filename is not a string or Path object.

    Returns:
        None
    """
    if filename is None:
        raise ValueError("Filename is required.")
    elif isinstance(filename, str):
        filename = Path(filename)
    elif not isinstance(filename, Path):
        raise ValueError("Filename must be a string or Path object.")

    df = pd.read_excel(filename, sheet_name="Sheet1")

    print(df)
    grand_total = {
        "Sales Demand Units": 0,
        "Total Receipt Plan Units": 0,
        "Planned Production Units": 0,
    }
    # Loop through the rows of the dataframe to get the actual grand total
    for _, row in df.iterrows():
        if row["Row Labels"] != "Grand Total":
            grand_total["Sales Demand Units"] += row["Sales Demand Units"]
            grand_total["Total Receipt Plan Units"] += row[
                "Total Receipt Plan Units"
            ]
            grand_total["Planned Production Units"] += row[
                "Planned Production Units"
            ]
        elif row["Row Labels"] == "Grand Total":
            expected = {
                "Sales Demand Units": row["Sales Demand Units"],
                "Total Receipt Plan Units": row["Total Receipt Plan Units"],
                "Planned Production Units": row["Planned Production Units"],
            }

    # Assert the actual grand total is equal to the expected grand total
    try:
        assert grand_total == expected
        print("OK: There is no difference.")
    except AssertionError as exeption:
        # Calculate the difference between the actual and expected grand total
        difference = {
            "Sales Demand Units": grand_total["Sales Demand Units"]
            - expected["Sales Demand Units"],
            "Total Receipt Plan Units": grand_total["Total Receipt Plan Units"]
            - expected["Total Receipt Plan Units"],
            "Planned Production Units": grand_total["Planned Production Units"]
            - expected["Planned Production Units"],
        }
        print(f"Error: {exeption}\nThere is difference of:\n{difference}")


def test_load_excel_file(filename: str | Path = None):
    """Load Excel file into a dataframe and print it."""
    if filename is None:
        raise ValueError("Filename is required.")
    elif isinstance(filename, str):
        filename = Path(filename)
    elif not isinstance(filename, Path):
        raise ValueError("Filename must be a string or Path object.")

    excel_file = pd.ExcelFile(filename)
    sheets = excel_file.sheet_names
    print(f"Excel file: {str(filename)}")
    print(f"There are {len(sheets)} Sheets: {sheets}")

    # loop through the sheets and print the dataframes
    for sheet in sheets:
        df = pd.read_excel(filename, sheet_name=sheet)
        print("--------------------")
        print(f"Sheet: {sheet}")
        print(df)


def main():
    """Main function"""
    excel_file = "C:/Users/rescobar/OneDrive - Carhartt Inc/Documents/git/powerbi-automate/data/Excel para automatización/Conectado a Supply.xlsx"
    test_load_excel_file(excel_file)


if __name__ == "__main__":
    main()
