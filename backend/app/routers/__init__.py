from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router
from app.routers.menus import router as menus_router

__all__ = ["auth_router", "orders_router", "menus_router"]