from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router

__all__ = ["auth_router", "orders_router"]