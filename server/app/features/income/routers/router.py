from fastapi import APIRouter

from app.features.income.routers.sub_routers.Get.get_income import router as get_income_router
from app.features.income.routers.sub_routers.Add.add_income import router as add_income_router
from app.features.income.routers.sub_routers.GetByID.get_income_by_id import router as get_income_by_id_router
from app.features.income.routers.sub_routers.Delete.delete_income import router as delete_income_router
from app.features.income.routers.sub_routers.Update.update_income import router as update_income_router

router = APIRouter()

router.include_router(get_income_router)
router.include_router(add_income_router)
router.include_router(get_income_by_id_router)
router.include_router(delete_income_router)
router.include_router(update_income_router)