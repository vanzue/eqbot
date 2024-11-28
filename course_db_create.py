import os
import json
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
models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    # Start a database session
    db = SessionLocal()

    try:
        # npc_data = """
        #             领导：擅长PUA，脾气很大。
        #             同事A：阿谀奉承，讨好领导。
        #             同事B：尖酸刻薄。
        #         """
        npc_json = {
            "npc1": {
                "name": "领导",
                "personality": "擅长PUA，脾气很大。"
            },
            "npc2": {
                "name": "同事A",
                "personality": "阿谀奉承，讨好领导。"
            },
            "npc3": {
                "name": "同事B",
                "personality": "尖酸刻薄。"
            }
        }
        npc_data = json.dumps(npc_json, ensure_ascii=False, indent=4)
        course_data = schemas.CoursesCreate(
                        course_dim = "掌控力",
                        course_level = 1,
                        prompt = """
                            今晚，我和三位同事——我的领导、同事A和同事B——在餐厅聚餐。通过轻松的日常对话，他们会考察我的情绪掌控力。每位同事初始都有一个心情值，每次对话都会使他们的心情加或减。

                            NPC的话题需要紧扣点菜，可以出现具体的菜品名称。
                            
                            另外，如果用户给出了一个合理的点菜方案，请让领导说出“你点的菜真不错”这句话。
                            """, 
                        title = "老板肚子里的蛔虫",
                        background = "在一个精致的会所包厢里，你与一位高层领导和两名同事共进晚餐。看似轻松的聚会，实际上领导在暗中观察你们，准备决定谁将参与重要项目。你必须讨好领导，同时平衡同事关系，因为一个小小的失误可能改变你的未来。",
                        npc = npc_data,
                        task = "一句话让每位同事心情愉悦:点出让每位同事满意的菜品",
                        image = None
                    )
        db_course_data = crud.create_course(db, course_data)
        print(f"Created Course: {db_course_data.id}")


    finally:
        db.close()

if __name__ == "__main__":
    main()