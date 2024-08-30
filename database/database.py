import os
from sqlalchemy import create_engine, text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()

user_name = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
server = os.getenv('DB_SERVER')
db_name = os.getenv('DB_NAME')

# DATABASE_URL = f"mssql+pyodbc://{user_name}:{db_password}@{server}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"
DATABASE_URL = f"mssql+pyodbc://{user_name}:{db_password}@{server}.database.windows.net:1433/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"

# CONNECTION_STR = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:eqmasterserver.database.windows.net,1433;Database=eqmasterdb;Uid=myadmin;Pwd="+ db_password +";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    with engine.connect() as connection:
        sql = text("SELECT * FROM dbo.PersonalInfo")
        result = connection.execute(sql)
        print(result.fetchone())

