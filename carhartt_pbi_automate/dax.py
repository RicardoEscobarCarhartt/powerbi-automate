"""This module contains functions to help parsing and transforming the DAX
query"""

from typing import Dict


def pass_args_to_dax_query(dax_query: str, args: Dict[str, str]) -> str:
    """Passes the arguments to the DAX query.
    Args:
        dax_query (str): The DAX query.
        args (Dict[str, str]): The arguments needed for the query to run.
    Returns:
        str: The DAX query with the arguments passed.
    """
    for key, value in args.items():
        # if value is a boolean
        if isinstance(value, bool):
            # replace the key with the string representation of the boolean
            dax_query = dax_query.replace(f"@{key}", f'"{str(value)}"')
        # if value is a number
        elif isinstance(value, (int, float)):
            # replace the key with the number
            dax_query = dax_query.replace(f"@{key}", str(value))
        elif isinstance(value, str):
            # replace the key with the string
            dax_query = dax_query.replace(f"@{key}", f'"{value}"')
        else:
            # replace the key with the string representation of the value
            dax_query = dax_query.replace(f"@{key}", f'"{str(value)}"')

    return dax_query
