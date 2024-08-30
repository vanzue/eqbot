import os
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
        # Create PersonalInfo
        # personal_info_data = schemas.PersonalInfoCreate(name="Jay Park", tag="idol", tag_description="black cat")
        # personal_info = crud.create_personal_info(db, personal_info_data)
        # print(f"Created PersonalInfo: {personal_info}")

        # Retrieve PersonalInfo by ID
        retrieved_personal_info = crud.get_personal_info(db, 1)
        print(f"Retrieved PersonalInfo: {retrieved_personal_info.name}")

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
        #     overall_suggestion="Continue with this approach"
        # )
        # eq_score = crud.create_eq_score(db, eq_score_data)
        # print(f"Created EQScore: {eq_score}")

        # # Retrieve EQScores by person_id
        # eq_scores = crud.get_eq_scores_by_person_id(db, personal_info.id)
        # print(f"Retrieved EQScores: {eq_scores}")

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
        # contact_data = schemas.ContactCreate(person_id=personal_info.id, name="Jane Smith", tag="Friend", relationship="Friend")
        # contact = crud.create_contact(db, contact_data)
        # print(f"Created Contact: {contact}")

        # # Retrieve Contacts by person_id
        # contacts = crud.get_contacts_by_person_id(db, personal_info.id)
        # print(f"Retrieved Contacts: {contacts}")

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

    finally:
        db.close()

if __name__ == "__main__":
    main()