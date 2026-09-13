from datetime import date as Date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_EXPENSE_AMOUNT = Decimal("9999999999.99")

class CreateRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    icon: str = Field(
        max_length=100, 
        default="",
    )

    amount: Decimal = Field(
        ...,
        gt=Decimal("0"),
        le=MAX_EXPENSE_AMOUNT,
        max_digits=12,
        decimal_places=2,

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