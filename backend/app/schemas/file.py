from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class FileCreate(BaseModel):

    upoaded_by : int
    file_path :str = Field(min_length=1,max_length=255)
    file_type : str = Field(min_length=1,max_length=50)
    file_name : str =Field(min_length=1,max_length=255)
    description : str |None =Field(default=None,max_length=500)


class FileResponse(BaseModel):

    id : int
    file_path : str
    file_name : str
    description : str | None
    file_type : str
    status : str

    model_config = ConfigDict(from_attributes=True)
