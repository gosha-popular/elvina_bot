__all__ = ('router',)

from aiogram import Router

from .commands import router as commands_router
from .interview import router as interview_router
from .menu import router as menu_router
from .echo import router as echo_router

router = Router(name=__name__)
router.include_routers(
    commands_router, menu_router, interview_router)

# Allways last - echo
router.include_router(echo_router)