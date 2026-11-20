from app.schemas.auth import LoginRequest, Token, TokenPayload
from app.schemas.user import UserResponse, UserBase, UserCreate, UserUpdate
from app.schemas.order import (
    OrderItemCreate,
    OrderDetailRead,
    QuoteRequest,
    QuoteResponse,
    EquipmentPenaltyCheck,
    OrderCreate,
    OrderUpdate,
    OrderRead,
    OrderStatusUpdate,
    OrderCancelRequest,
)
from app.schemas.menu import (
    RefItem,
    PlatBase,
    PlatRead,
    MenuBase,
    MenuCreate,
    MenuUpdate,
    MenuListItem,
    MenuDetail,
    CatalogueFilters,
)
from app.schemas.stats import (
    GlobalKPIs,
    TopMenuStat,
    MonthlyRevenueStat,
    AdminStatsResponse,
)
from app.schemas.avis import (
    AvisNotes,
    AvisCreate,
    AvisModerationUpdate,
    AvisRead,
)
from app.schemas.horaire import (
    HoraireRead,
    HoraireUpdate,
)
from app.schemas.contact import (
        ContactCreate,
        ContactRead,
)

__all__ = [
    "LoginRequest",
    "Token",
    "TokenPayload",
    "UserResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "OrderItemCreate",
    "OrderDetailRead",
    "QuoteRequest",
    "QuoteResponse",
    "EquipmentPenaltyCheck",
    "OrderCreate",
    "OrderUpdate",
    "OrderRead",
    "OrderStatusUpdate",
    "OrderCancelRequest",
    "RefItem",
    "PlatBase",
    "PlatRead",
    "MenuBase",
    "MenuCreate",
    "MenuUpdate",
    "MenuListItem",
    "MenuDetail",
    "CatalogueFilters",
    "GlobalKPIs",
    "TopMenuStat",
    "MonthlyRevenueStat",
    "AdminStatsResponse",
    "AvisNotes",
    "AvisCreate",
    "AvisModerationUpdate",
    "AvisRead",
    "HoraireRead",
    "HoraireUpdate",
    "ContactCreate",
    "ContactRead",
]
