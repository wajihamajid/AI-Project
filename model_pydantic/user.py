from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The email address of the user")
    password_hash: str = Field(..., description="The hashed password of the user")

class UserRead(BaseModel):
    id: int = Field(..., description="The unique idenitifier of the user")
    email: EmailStr = Field(..., description="The email address of the user")

    class config():
        from_attributes = True
        extra = "forbid"