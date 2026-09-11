from pydantic import Field, field_validator

from app.shared.schemas.UpdateRequest.update_request_base import UpdateRequestBase


class UpdateExpenseRequest(UpdateRequestBase):
    category: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value):
        if value is None:
            raise ValueError("Category cannot be null")

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError(
                    "Category cannot be empty or whitespace"
                )

        return value