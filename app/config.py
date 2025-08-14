from dotenv import load_dotenv
import os
import urllib

load_dotenv()
raw = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=PRO-GYE-122\\ETC;"
    "DATABASE=BB_Authentication;"
    "UID=sa;"
    "PWD=etc12345!I;"
    "Trust_Connection=yes;"
)
params = urllib.parse.quote_plus(raw)

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL",
    f"mssql+pyodbc:///?odbc_connect={params}"
)
# DATABASE_URL  = os.getenv("SQLALCHEMY_DATABASE_URL")
SECRET_KEY    = os.getenv("SECRET_KEY")
ALGORITHM     = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
