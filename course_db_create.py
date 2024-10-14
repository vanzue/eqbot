import os, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import crud, models, schemas
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv

load_dotenv()

user_name = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
server = os.getenv('DB_SERVER')
db_name = os.getenv('DB_NAME')

DATABASE_URL = f"mssql+pyodbc://{user_name}:{db_password}@{server}.database.windows.net:1433/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create all tables
models.Base.metadata.create_all(bind=engine)

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