from datetime import date as Date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UpdateRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float | None = Field(
        default=None,
        gt=0,
        strict=True,
    )

    date: Date | None = Field(
        default=None
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

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, value):
        if value is None:
            raise ValueError(
                "Description cannot be null"
            )

        if isinstance(value, str):
            value = value.strip()

        return value