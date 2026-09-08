from fastapi import APIRouter

from app.features.expense.routers.sub_routers.Get.get_expense import router as get_expense_router
from app.features.expense.routers.sub_routers.Add.add_expense import router as add_expense_router
from app.features.expense.routers.sub_routers.GetByID.get_expense_by_id import router as get_expense_by_id_router
from app.features.expense.routers.sub_routers.Delete.delete_expense import router as delete_expense_router
from app.features.expense.routers.sub_routers.Update.update_expense import router as update_expense_router

router = APIRouter()

router.include_router(get_expense_router)
router.include_router(add_expense_router)
router.include_router(get_expense_by_id_router)
router.include_router(delete_expense_router)
router.include_router(update_expense_router)