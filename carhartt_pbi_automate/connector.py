"""This module creates connections to the SQL server database, Power BI, and
Microsoft Teams."""

import adodbapi
from sqlalchemy import create_engine


def get_edw_connection(
    server="DBNSQLQNET",
    database="CarharttDw",
    driver="ODBC Driver 17 for SQL Server",
):
    """Returns a connection to the CarharttDw database."""
    connection_string = f"mssql+pyodbc://{server}/{database}?driver={driver}&trusted_connection=yes"
    engine = create_engine(connection_string, fast_executemany=True)
    return engine.connect()


def get_bi_connection(
    server="powerbi://api.powerbi.com/v1.0/myorg/BI-WIP Data Quality & Support",
    database="Data Flow Metrics",
):
    """Returns a connection to the CarharttBI database."""
    # POWER BI CONNECTION ####################
    connection_string = (
        f"Provider=MSOLAP.8; Data Source={server}; Initial Catalog={database};"
    )
    return adodbapi.connect(connection_string)
