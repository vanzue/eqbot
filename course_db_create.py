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
        npc_json = {
            "npc1": {
                "name": "Jason",
                "personality": "A results-driven colleague from another department, Jason is direct and can become impatient under pressure. He values quick solutions and gets frustrated when meetings don’t progress as expected, though his intent is to push projects forward efficiently.",
                "voice": "en-US-DavisNeural",
                "style": "chat",
                "rate": "0%"
            },
            "npc2": {
                "name": "Sam",
                "personality": "An introverted and detail-oriented team member who prefers to take time to process information before speaking. Sam is sensitive to tense situations and tends to withdraw when feeling pressured or uncomfortable in group discussions.",
                "voice": "en-US-JasonNeural",
                "style": "friendly",
                "rate": "10%"
            },
            "npc3": {
                "name": "Anna",
                "personality": "An optimistic and easy-going team member who is rarely affected by tense atmospheres. She tends to remain positive and often approaches problem-solving in a light-hearted manner, but she doesn't always sense the urgency in the room.",
                "voice": "en-US-JennyNeural",
				"style": "chat",
				"rate": "10%",
            }
        }
        npc_data = json.dumps(npc_json, ensure_ascii=False, indent=4)
        print(npc_data)
        crud.update_course_npc(db, 4, npc_data)
        # course_data = schemas.CoursesCreate(
        #                 course_dim = "self_regulation",
        #                 course_level = 1,
        #                 prompt = """
        #                     "You are a master of emotional quotient. You will observe conversations in a scenario and you will help npc generate dialog, evaluate my EQ and help drive the progress of conversation.   **Background of the conversation**: Today, I'm attending a cross-department communication meeting to discuss an urgent issue in Jason's project. Jason, from another department, is seeking collaboration and ideas for a solution. He asks the team (Sam, Anna, and user) for feedback, but the room falls into silence as no one responds immediately. Jason, feeling frustrated, raises his voice slightly, saying, \"Why isn’t anyone sharing ideas? I thought this was a team effort!\" The atmosphere becomes tense. Sam appears uncomfortable, while Anna remains relaxed, unaffected by the tension.
        #                     """, 
        #                 title = "Managing Tensions in a Meeting2",
        #                 background = "Jason joins your team meeting, frustrated by the lack of feedback on his project.Tension rises as Sam feels uneasy, and Anna stays clam. How will you respond to ease the situation?",
        #                 location = "Meeting Room",
        #                 npc = npc_data,
        #                 locale = "en",
        #                 task = "Cheee up Sam while avoiding further infuriating Jason:Encourage teammates to engage and get at least one to say, \"I agree with you\"",
        #                 image = None
        #             )
        # db_course_data = crud.create_course(db, course_data)
        # print(f"Created Course: {db_course_data.id}")

        # person_course_data = schemas.PersonalInfoCoursesCreate(
        #     user_id=1,
        #     course_id=3,
        #     course_dim="self_regulation",
        #     course_level=1,
        #     status="complete",
        #     result=2,
        #     comment1="comment for testing",
        #     comment2="comment for testing",
        #     comment3="comment for testing",
        #     locale="en"
        # )
        # db_person_course = crud.create_personal_info_course(db, person_course_data)
        # print(db_person_course)


    finally:
        db.close()

if __name__ == "__main__":
    main()