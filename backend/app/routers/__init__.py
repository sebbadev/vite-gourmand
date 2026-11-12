from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router
from app.routers.menus import router as menus_router
from app.routers.stats import router as stats_router
from app.routers.plats import router as plats_router
from app.routers.avis import router as avis_router
from app.routers.admin_users import router as admin_users_router
from app.routers.horaires import router as horaires_router
from app.routers.contact import router as contact_router

__all__ = [
    "auth_router",
    "orders_router",
    "menus_router",
    "stats_router",
    "plats_router",
    "avis_router",
    "admin_users_router",
    "horaires_router",
    "contact_router",
]