from datetime import date as Date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateExpenseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(..., gt=0)

    date: Date = Field(...)

    category: str = Field(
        ...,
        max_length=100
    )

    description: str = Field(
        default="",
        max_length=500
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Category cannot be empty or whitespace")

        return value

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value):
        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Date cannot be empty or whitespace")

        return value