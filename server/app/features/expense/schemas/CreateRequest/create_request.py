from pydantic import Field, field_validator

from app.shared.schemas.CreateRequest.create_request_base import CreateRequestBase

class CreateExpenseRequest(CreateRequestBase):
    category: str = Field(
        ...,
        max_length=100
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Category cannot be empty or whitespace")

        return value