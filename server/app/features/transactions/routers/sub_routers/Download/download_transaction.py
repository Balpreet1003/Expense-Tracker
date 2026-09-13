from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.features.auth.dependencies.auth import get_current_user
from app.features.auth.models.user import User

from app.features.transactions.services.Download.download_transaction_service import (
    download_transactions,
)


router = APIRouter()


@router.get(
    "/transactions/download",
    status_code=status.HTTP_200_OK,
)
def download_transaction_file(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    excel_file = download_transactions(
        db=db,
        current_user=current_user,
    )

    headers = {
        "Content-Disposition": (
            'attachment; filename="transactions.xlsx"'
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