from pydantic import BaseModel, EmailStr, Field


class EmailLogin(BaseModel):
    username: EmailStr | None = Field(default=None)
    password: str
