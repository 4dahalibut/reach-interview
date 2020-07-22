from typing import Tuple
import os

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.redis import RedisBackend
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, SessionLocal
from app.mailer import send_email

models.Base.metadata.create_all(bind=engine)


class OurNotFoundException(HTTPException):
    def __init__(self, message):
        super().__init__(status_code=404, detail=message)


async def not_found(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"message": "nope"}),
    )


async def AUTH_FUNCTION(scope) -> Tuple[str, str]:
    """
    Resolve the user's unique identifier and the user's group from ASGI SCOPE.

    If there is no user information, it should raise `EmptyInformation`.
    If there is no group information, it should return "default".
    """
    return "1", "default"


app = FastAPI(exception_handlers={404: not_found})

if os.getenv('ENVIRONMENT') != "testing":
    app.add_middleware(
        RateLimitMiddleware,
        authenticate=AUTH_FUNCTION,
        backend=RedisBackend(),
        config={
            r"^/person": [Rule(second=1), Rule(group="default")],
            r"^/": [Rule(minute=5), Rule(group="default")],
        },
    )


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
