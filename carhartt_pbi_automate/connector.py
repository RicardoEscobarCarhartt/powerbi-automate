"""This module creates connections to the SQL server database, Power BI, and
Microsoft Teams."""

import adodbapi
from sqlalchemy import create_engine


def get_edw_connection(
    server: str = "DBNSQLQNET",
    database: str = "CarharttDw",
    driver: str = "ODBC Driver 17 for SQL Server",
) -> adodbapi.Connection:
    """Returns a connection to the CarharttDw database.
    Args:
        server (str): The server name.
        database (str): The database name.
        driver (str): The driver name.
    Returns:
        adodbapi.Connection: The connection to the CarharttDw database."""
    connection_string = f"mssql+pyodbc://{server}/{database}?driver={driver}&trusted_connection=yes"
    engine = create_engine(connection_string, fast_executemany=True)
    return engine.connect()


def get_bi_connection(
    server: str = "powerbi://api.powerbi.com/v1.0/myorg/BI-WIP Data Quality & Support",
    database: str = "Data Flow Metrics",
) -> adodbapi.Connection:
    """Returns a connection to the Carhartt Power BI database.
    Args:
        server (str): The server name.
        database (str): The database name.
    Returns:
        adodbapi.Connection: The connection to the Carhartt Power BI database."""
    connection_string = (
        f"Provider=MSOLAP.8; Data Source={server}; Initial Catalog={database};"
    )
    return adodbapi.connect(connection_string)
