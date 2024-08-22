from sqlalchemy.orm import Session
from database import database, models, schemas
from database.crud import create_personal_info, get_personal_info

# Initialize the database
models.Base.metadata.create_all(bind=database.engine)


def main():
    # Start a new database session
    db: Session = database.SessionLocal()

    try:
        # Create a new PersonalInfo record
        new_person = schemas.PersonalInfoCreate(name="John Doe")
        created_person = create_personal_info(db, new_person)
        print(f"Created Person: {created_person.id} - {created_person.name}")

        # Fetch the created record by ID
        fetched_person = get_personal_info(db, created_person.id)
        if fetched_person:
            print(
                f"Fetched Person: {fetched_person.id} - {fetched_person.name}")
        else:
            print("Person not found")

    finally:
        # Close the database session
        db.close()


if __name__ == "__main__":
    main()
