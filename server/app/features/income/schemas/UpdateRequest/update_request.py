from datetime import date as Date
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UpdateIncomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float | None = Field(
        default=None,
        gt=0
    )

    date: Date | None = None

    source: str | None = Field(
        default=None,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value):
        if value is None:
            raise ValueError("Amount cannot be null")

        return value

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value):
        if value is None:
            raise ValueError("Date cannot be null")

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError(
                    "Date cannot be empty or whitespace"
                )

        return value

    @field_validator("source", mode="before")
    @classmethod
    def validate_source(cls, value):
        if value is None:
            raise ValueError("Source cannot be null")

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError(
                    "Source cannot be empty or whitespace"
                )

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if value is None:
            raise ValueError(
                "Description cannot be null"
            )

        if isinstance(value, str):
            value = value.strip()

        return value