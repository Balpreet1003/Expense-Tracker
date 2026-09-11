from pydantic import Field, field_validator

from app.shared.schemas.UpdateRequest.update_request_base import UpdateRequestBase


class UpdateIncomeRequest(UpdateRequestBase):
    source: str | None = Field(
        default=None,
        max_length=100,
    )

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