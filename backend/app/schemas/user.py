from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# What the user SENDS to register

class UserCreate(BaseModel):
    name : str = Field(min_length=1,max_length=50)
    username : str = Field(min_length=1,max_length=50)
    email : EmailStr
    password : str = Field(min_length=8,max_length=50)


# What the API SENDS BACK (never includes the password)
class UserResponse(BaseModel):

    id :int
    name : str
    username : str
    email : EmailStr
    created_at : datetime 

    model_config = ConfigDict(from_attributes=True)


