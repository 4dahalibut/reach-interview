from sqlalchemy.orm import Session

from . import models, schemas


# Both email and ID should be unique
def get_person_by_email(db: Session, email: str):
    return db.query(models.Person).filter(models.Person.email == email).first()


def get_person_by_id(db: Session, person_id: int):
    return db.query(models.Person).filter(models.Person.id == person_id).first()


def create_person(db: Session, person: schemas.PersonSignUp):
    db_person = models.Person(
        email=person.email, name=person.name, description=person.description
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def update_description(db: Session, person: schemas.Person):
    # TODO: What if person tries to update other things? It will silently not happen
    db_person = get_person_by_id(db, person.id)
    db_person.description = person.description
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


def mark_person_emailed(db: Session, email: str):
    person = db.query(models.Person).filter(models.Person.email == email).first()
    person.signup_email_success = True
    db.commit()
