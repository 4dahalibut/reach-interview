from sqlalchemy.orm import Session

from . import models, schemas


def get_person_by_email(db: Session, email: str):
    return db.query(models.Person).filter(models.Person.email == email).first()


def create_person(db: Session, user: schemas.PersonSignUp):
    db_user = models.Person(
        email=user.email, name=user.name, description=user.description
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_description(db: Session, user: schemas.Person):
    # TODO: What if user tries to update other things? It will silently not happen
    db_user = get_person_by_id(db, user.id)
    db_user.description = user.description
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def mark_person_emailed(db: Session, email: str):
    person = db.query(models.Person).filter(models.Person.email == email).first()
    person.signup_email_success = True
    db.commit()


def get_person_by_id(db: Session, user_id: int):
    return db.query(models.Person).filter(models.Person.id == user_id).first()
