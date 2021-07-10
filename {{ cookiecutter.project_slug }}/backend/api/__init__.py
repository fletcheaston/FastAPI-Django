from fastapi import APIRouter

from .items import router as item_router
from .users import router as user_router

router = APIRouter()

router.include_router(item_router)
router.include_router(user_router)
