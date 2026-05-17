from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):

    fullname: str

    designation: str

    email: EmailStr

    mobile: str

    organization: str

    country: str

    password: str


class LoginSchema(BaseModel):

    email: EmailStr

    password: str
