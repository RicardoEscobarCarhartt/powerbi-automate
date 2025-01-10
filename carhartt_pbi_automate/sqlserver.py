"""
Connects to a SQL database using pyodbc with a trusted connection
"""
import pyodbc


SERVER = 'DBNSQLPNET'
DATABASE = 'CarharttDw'
DRIVER = 'ODBC Driver 17 for SQL Server'

connectionString = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

conn = pyodbc.connect(connectionString)

SQL_QUERY = """SELECT GETDATE() AS date_time;"""

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
for r in records:
    print(f"Date Time: {r.date_time}")
