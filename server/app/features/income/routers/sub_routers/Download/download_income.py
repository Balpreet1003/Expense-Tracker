from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

from app.features.income.services.Download.download_income_service import (
    download_incomes,
)


router = APIRouter()


@router.get(
    "/income/download",
    status_code=status.HTTP_200_OK,
)
def download_income_file(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    excel_file = download_incomes(
        db=db,
        current_user=current_user,
    )

    headers = {
        "Content-Disposition": (
            'attachment; filename="incomes.xlsx"'
        )
    }

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers=headers,
    )