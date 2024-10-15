import os
import pyodbc, struct
from database import crud, models, schemas
from azure import identity
from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine, event, text, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv

load_dotenv()

# Define your Azure SQL Database details
server = os.getenv('DATABASE_SERVER')
database = os.getenv('DATABASE_NAME')

SQL_COPT_SS_ACCESS_TOKEN = 1256  # As defined in msodbcsql.h

def inject_azure_credential(credential, engine, token_url='https://database.windows.net/'):
    @event.listens_for(engine, 'do_connect')
    def do_connect(dialect, conn_rec, cargs, cparams):
        token = credential.get_token(token_url).token.encode('utf-16-le')
        token_struct = struct.pack(f'=I{len(token)}s', len(token), token)
        attrs_before = cparams.setdefault('attrs_before', {})
        attrs_before[SQL_COPT_SS_ACCESS_TOKEN] = bytes(token_struct)
        return dialect.connect(*cargs, **cparams)

# Use DefaultAzureCredential or any other Azure credentials
creds = DefaultAzureCredential()

# Create the SQLAlchemy engine
engine = create_engine(
    'mssql+pyodbc:///?odbc_connect=DRIVER={ODBC Driver 18 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'TrustServerCertificate=yes;'
    'Encrypt=yes'
)

# Inject Azure credentials into the engine
inject_azure_credential(creds, engine)

metadata = MetaData(schema='dbo')

Base = declarative_base(metadata=metadata)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    # Start a database session
    db = SessionLocal()

    try:
        course_data = schemas.CoursesCreate(
                        course_type = "情绪掌控力",
                        course_level = 1,
                        prompt = """
                            你是一位情绪掌控大师。今晚，我和三位同事——我的领导、同事A和同事B——在餐厅聚餐。通过轻松的日常对话，他们会考察我的情绪掌控力。每位同事初始都有一个心情值，每次对话都会使他们的心情加或减。请根据以下人物性格生成对话：请根据以下人物性格生成对话：

                            领导：擅长PUA，脾气很大。
                            同事A：阿谀奉承，讨好领导。
                            同事B：尖酸刻薄。
                            """
                        )
        db_course_data = crud.create_course(db, course_data)
        print(f"Created Course: {db_course_data.id}")


    finally:
        db.close()

if __name__ == "__main__":
    main()