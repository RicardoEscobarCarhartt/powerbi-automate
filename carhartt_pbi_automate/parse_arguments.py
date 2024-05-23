"""This module contains functions to help parsing script arguments."""

import argparse


def parse_arguments() -> argparse.Namespace:
    """Parses the script arguments."""
    parser = argparse.ArgumentParser(description="My script with arguments")
    parser.add_argument(
        "--daxfile",
        type=str,
        default=r"C:\Users\rescobar\OneDrive - Carhartt Inc\Documents\git\powerbi-automate\queries\supply.dax",
        help="File path to DAX query",
    )
    parser.add_argument(
        "--sqlfile",
        type=str,
        default=r"C:\Users\rescobar\OneDrive - Carhartt Inc\Documents\git\powerbi-automate\queries\supply.sql",
        help="File path to SQL query")

    args = parser.parse_args()
    return args
