from datetime import date as Date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_EXPENSE_AMOUNT = Decimal("9999999999.99")

class UpdateRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    amount: Decimal | None = Field(
        default=None,
        decimal_places=2,
        gt=Decimal("0"),
        le=MAX_EXPENSE_AMOUNT,
        max_digits=12,
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

    @field_validator("icon", mode="before")
    @classmethod
    def validate_icon(cls, value):
        if value is None:
            raise ValueError(
                "Icon cannot be null"
            )

        return value