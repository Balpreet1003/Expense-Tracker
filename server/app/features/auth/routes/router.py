from fastapi import APIRouter

from app.features.auth.routes.sub_routes.register_user import router as register_router
from app.features.auth.routes.sub_routes.login import router as login_router
from app.features.auth.routes.sub_routes.profile import router as profile_router

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


router.include_router(login_router)
router.include_router(register_router)
router.include_router(profile_router)