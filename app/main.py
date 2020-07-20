from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, SessionLocal
from .mailer import send_email

models.Base.metadata.create_all(bind=engine)


class OurNotFoundException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


async def not_found(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"message": "nope"}),
    )


app = FastAPI(exception_handlers={404: not_found})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/person/")
async def sign_person_up(
    person: schemas.PersonSignUp,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    db_person = crud.get_person_by_email(db, email=person.email)
    if db_person:
        raise HTTPException(status_code=400, detail="Email already registered")
    person = crud.create_person(db, person)
    background_tasks.add_task(
        send_email, person.email, person.name, message="Thanks for signing up", db=db
    )
    return person


@app.put("/person/")
async def edit_person(
    person: schemas.Person,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if crud.get_person_by_id(db, person_id=person.id) is None:
        raise OurNotFoundException("ID not found")
    person = crud.update_description(db, person)
    background_tasks.add_task(
        send_email,
        person.email,
        person.name,
        message="Your info has been changed",
        db=db,
    )
    return person


@app.get("/person/{person_id}", response_model=schemas.Person)
def fetch_person(person_id: int, db: Session = Depends(get_db)):
    person = crud.get_person_by_id(db, person_id=person_id)
    if person is None:
        raise OurNotFoundException("That person isn't in our database!")
    return person
