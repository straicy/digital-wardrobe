from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    "DATABASE=digital_wardrobe;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(
    URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
)