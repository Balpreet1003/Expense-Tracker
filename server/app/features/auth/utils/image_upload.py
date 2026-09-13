from app.core.Cloudinary import cloudinary
import cloudinary.uploader

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
}


def upload_profile_image(
    image: UploadFile,
) -> str:

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only JPG, JPEG, and PNG images are allowed"
            ),
        )

    try:

        upload_result = (
            cloudinary.uploader.upload(
                image.file,
                folder=(
                    "expense_tracker-profile_images"
                ),
                transformation=[
                    {
                        "width": 300,
                        "height": 300,
                        "crop": "limit",
                    }
                ],
            )
        )

        return upload_result["secure_url"]

    except Exception as error:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Failed to upload profile image",
        )