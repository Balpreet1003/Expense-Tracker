from datetime import date as Date
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CreateIncomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(..., gt=0)

    date: Date = Field(...)

    source: str = Field(
        ...,
        max_length=100
    )

    description: str = Field(
        default="",
        max_length=500
    )

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if value is None:
            raise ValueError("Source cannot be null")

        if isinstance(value, str):
            value = value.strip()

        if not value:
            raise ValueError("Source cannot be empty or whitespace")

        return value

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