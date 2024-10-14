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
server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')

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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData(schema='dbo')

Base = declarative_base(metadata=metadata)
# Create all tables
models.Base.metadata.create_all(bind=engine)


def main():
    # Start a database session
    db = SessionLocal()

    try:
        # Create PersonalInfo
        issues = ["沟通不畅", "团队合作"]
        concerns = ", ".join(issues)

        personal_info_data = schemas.PersonalInfoCreate(
                                name="Jay Park", 
                                gender="male",
                                tag=None, 
                                tag_description="黑猫",
                                job_level="Junior", 
                                issues=concerns,
                                job_id="ba94c32e-aa33-4c5d-8cda-effb8c9fda90"
                                )
        personal_info = crud.create_personal_info(db, personal_info_data)
        print(f"Created PersonalInfo: {personal_info.id}")

        # Update PersonalInfo
        # personal_info = crud.get_personal_info_by_job_id(db, "d508fc86-948c-42a4-8b98-c415d9f3c5e3")
        # print(f"Retrieved PersonalInfo: {personal_info.name}")
        # personal_info_update = schemas.PersonalInfoUpdate(
        #     tag="情绪小火山",
        #     tag_description="情绪小火山tag_description"
        # )
        # updated_personal_info = crud.update_personal_info_by_name(db, personal_info.name, personal_info_update)
        # print(f"Updated PersonalInfo: {updated_personal_info.tag}")

        # Retrieve PersonalInfo by ID
        # for _ in range(10):
        #     retrieved_personal_info = crud.get_personal_info(db, 1)
        #     print(f"Retrieved PersonalInfo: {retrieved_personal_info.id}")
        # personal_info = crud.get_personal_info_by_job_id(db, "aa94c32e-aa33-4c5d-8cda-effb8c9fda90")
        # print(f"Retrieved PersonalInfo: {personal_info.name}")

        # Create EQScore
        # eq_score_data = schemas.EQScoreCreate(
        #     # person_id=personal_info.id,
        #     person_id=1,
        #     dimension1_score=85,
        #     dimension1_detail="Detail 1",
        #     dimension2_score=90,
        #     dimension2_detail="Detail 2",
        #     dimension3_score=75,
        #     dimension3_detail="Detail 3",
        #     dimension4_score=80,
        #     dimension4_detail="Detail 4",
        #     dimension5_score=95,
        #     dimension5_detail="Detail 5",
        #     summary="Good overall",
        #     detail="Detailed explanation",
        #     overall_suggestion="Continue with this approach",
        #     job_id="aa94c32e-aa33-4c5d-8cda-effb8c9fda90"
        # )
        # eq_score = crud.create_eq_score(db, eq_score_data)
        # print(f"Created EQScore: {eq_score}")

        # # Retrieve EQScores by person_id
        # eq_scores = crud.get_eq_scores_by_person_id(db, personal_info.id)
        # print(f"Retrieved EQScores: {eq_scores}")
        # eq_scores = crud.get_eq_scores_by_job_id(db, "aa94c32e-aa33-4c5d-8cda-effb8c9fda90")
        # print(f"Retrieved EQScores: {eq_scores.summary}")

        # # Create Course
        # course_data = schemas.CoursesCreate(course_name="Emotional Intelligence 101", course_description="A beginner course on EQ.")
        # course = crud.create_course(db, course_data)
        # print(f"Created Course: {course}")

        # # Assign Course to PersonalInfo
        # personal_info_course_data = schemas.PersonalInfoCoursesCreate(person_id=personal_info.id, course_id=course.id)
        # personal_info_course = crud.add_course_to_personal_info(db, personal_info_course_data)
        # print(f"Assigned Course to PersonalInfo: {personal_info_course}")

        # # Retrieve PersonalInfoCourses by person_id
        # personal_info_courses = crud.get_personal_info_courses(db, personal_info.id)
        # print(f"Retrieved PersonalInfoCourses: {personal_info_courses}")

        # # Create Contact
        # contact_data = schemas.ContactCreate(person_id=1, name="Sunoo", tag="摸鱼高手", contact_relationship="Subordinate")
        # contact = crud.create_contact(db, contact_data)
        # print(f"Created Contact: {contact}")

        # # Retrieve Contacts by person_id
        # contacts = crud.get_contacts_by_person_id(db, personal_info.id)
        # print(f"Retrieved Contacts: {contacts}")

        # contacts = crud.get_contacts_by_person_name(db, "Jay Park")
        # print(f"Retrieved Contacts: {contacts}")
        # for contact in contacts:
        #     print(f"Contact: {contact.name}")

        # # Create ChatRecord
        # chat_record_data = schemas.ChatRecordsCreate(person_id=personal_info.id, contact_id=contact.id, chat_time="2024-08-26 14:00:00", chat_content="Hello, how are you?")
        # chat_record = crud.create_chat_record(db, chat_record_data)
        # print(f"Created ChatRecord: {chat_record}")

        # # Retrieve ChatRecords by person_id
        # chat_records = crud.get_chat_records_by_person_id(db, personal_info.id)
        # print(f"Retrieved ChatRecords: {chat_records}")

        # # Clean up: Delete created records
        # crud.delete_chat_record(db, chat_record.id)
        # crud.delete_contact(db, contact.id)
        # crud.remove_course_from_personal_info(db, personal_info.id, course.id)
        # crud.delete_course(db, course.id)
        # crud.delete_eq_score(db, eq_score.id)
        # crud.delete_personal_info(db, personal_info.id)

        # print("Cleaned up all created records.")

        # analysis = schemas.SubordinateAnalysisCreate(
        #             contact_id=1,
        #             relationship_analysis="你与这位同事的关系较为紧张，沟通中存在信息不对称和误解，表现出一定的争执和不满。",
        #             work_compatibility="你们的共事契合度较低，沟通中缺乏明确的职责分工和有效的协作，需要加强沟通与职责明确。",
        #             cunning_index="65, 同事在对话中表现出一定的防备和推诿责任的倾向，可能会在特定情况下保护自己的利益。",
        #             work_personality="同事表现出较为谨慎和防御的性格特征，倾向于明确职责范围，不愿多承担额外的责任。",
        #             interests="从聊天记录来看，同事对特定话题没有明显的兴趣，更多的是关注职责的明确和自身的工作范围。",
        #             bad_colleague_risk="同事表现出推诿责任的行为，但没有明显的恶意或破坏性行为迹象，需进一步观察其在团队中的表现。"
        #             )
        # crud.create_subordinate_analysis(db, analysis)

    finally:
        db.close()

if __name__ == "__main__":
    main()