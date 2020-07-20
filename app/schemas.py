from typing import Optional

from pydantic import BaseModel, constr, EmailStr


class PersonSignUp(BaseModel):
    email: EmailStr
    name: str
    description: Optional[str]


class Person(BaseModel):
    id: int
    name: constr(min_length=2, max_length=40)
    email: EmailStr
    description: Optional[constr(min_length=1, max_length=500)]
    signup_email_success: bool

    class Config:
        orm_mode = True
