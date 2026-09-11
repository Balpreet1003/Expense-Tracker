from fastapi import APIRouter

from app.features.transactions.routers.sub_routers.Add.add_transaction import router as add_transaction_router
from app.features.transactions.routers.sub_routers.Get.get_transaction import router as get_transaction_router
from app.features.transactions.routers.sub_routers.Delete.delete_transaction import router as delete_transaction_router
from app.features.transactions.routers.sub_routers.Update.update_transaction import router as update_transaction_router
from app.features.transactions.routers.sub_routers.GetByID.get_transaction_by_id import router as get_transaction_by_id_router

router = APIRouter()

router.include_router(add_transaction_router)
router.include_router(get_transaction_router)
router.include_router(delete_transaction_router)
router.include_router(update_transaction_router)
router.include_router(get_transaction_by_id_router)