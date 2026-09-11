from pydantic import Field, field_validator

from app.shared.schemas.CreateRequest.create_request_base import CreateRequestBase

class CreateIncomeRequest(CreateRequestBase):
    source: str = Field(
        ...,
        max_length=100
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