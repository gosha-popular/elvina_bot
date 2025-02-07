__all__ = ('router',)

from aiogram import Router

from .admin_commands import router as admin_commands_router
from .user_commands import router as user_commands_router

router = Router(name=__name__)
router.include_routers(
    admin_commands_router, user_commands_router,

)