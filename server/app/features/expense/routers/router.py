from fastapi import APIRouter

from app.features.expense.routers.sub_routers.get_expense import router as get_expense_router
from app.features.expense.routers.sub_routers.add_expense import router as add_expense_router
from app.features.expense.routers.sub_routers.get_expense_by_id import router as get_expense_by_id_router
from app.features.expense.routers.sub_routers.delete_expense import router as delete_expense_router
from app.features.expense.routers.sub_routers.update_expense import router as update_expense_router

router = APIRouter()

router.include_router(get_expense_router)
router.include_router(add_expense_router)
router.include_router(get_expense_by_id_router)
router.include_router(delete_expense_router)
router.include_router(update_expense_router)