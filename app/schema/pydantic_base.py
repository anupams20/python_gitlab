from uuid import UUID

from pydantic import BaseModel, validator, field_validator


class PydanticOutBase(BaseModel):
    id: UUID

    @classmethod
    @field_validator("id", mode="before")
    def convert_uuid_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
