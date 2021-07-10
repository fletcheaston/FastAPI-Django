from fastapi import APIRouter

from .auth import router as auth_router
from .items import router as item_router
from .users import router as user_router

router = APIRouter()

router.include_router(item_router)
router.include_router(user_router)
router.include_router(auth_router)
