from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, SessionLocal
from .mailer import send_email

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class OurNotFoundException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/person/")
async def sign_person_up(
    user: schemas.PersonSignUp,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_user = crud.get_person_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_person(db, user)
    background_tasks.add_task(
        send_email, user.email, user.name, message="Thanks for signing up", db=db
    )
    return user


@app.put("/person/")
async def edit_person(
    user: schemas.Person,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if crud.get_person_by_id(db, user_id=user.id) is None:
        raise OurNotFoundException("ID not found")
    user = crud.update_description(db, user)
    background_tasks.add_task(
        send_email, user.email, user.name, message="Your info has been changed", db=db
    )
    return user


@app.get("/person/{user_id}", response_model=schemas.Person)
def read_users(user_id: int, db: Session = Depends(get_db)):
    person = crud.get_person_by_id(db, user_id=user_id)
    if person is None:
        raise OurNotFoundException("That person isn't in our database!")
    return person
