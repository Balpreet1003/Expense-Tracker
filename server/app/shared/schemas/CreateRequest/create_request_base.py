from datetime import date as Date
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CreateRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(
        ...,
        gt=0,
        strict=True,
    )

    date: Date = Field(...)

    description: str = Field(
        default="",
        max_length=500
    )

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value):
        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Date cannot be empty or whitespace")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if isinstance(value, str):
            value = value.strip()

        return value