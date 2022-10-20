from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    first_name: Optional[str]
    email: Optional[EmailStr] = None
    is_admin: bool = False

class UserSignupRequest(UserBase):
    email: EmailStr
    password: str

class UserSignupResponse(UserBase):
    ...
    

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


