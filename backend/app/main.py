from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db, get_mongo_db
from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router
from app.routers.menus import router as menus_router
from app.routers.stats import router as stats_router
from app.routers.plats import router as plats_router
from app.routers.avis import router as avis_router
from app.routers.admin_users import router as admin_users_router
from app.routers.horaires import router as horaires_router
from app.routers.contact import router as contact_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API RESTful traiteur événementiel (FastAPI, PostgreSQL, MongoDB)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS dynamique
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Branchement des routeurs métier
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)
app.include_router(menus_router, prefix=settings.API_V1_STR)
app.include_router(stats_router, prefix=settings.API_V1_STR)
app.include_router(plats_router, prefix=settings.API_V1_STR)
app.include_router(avis_router, prefix=settings.API_V1_STR)
app.include_router(admin_users_router, prefix=settings.API_V1_STR)
app.include_router(horaires_router, prefix=settings.API_V1_STR)
app.include_router(contact_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
async def health_check(
    db: Session = Depends(get_db),
    mongo = Depends(get_mongo_db)
):
    pg_status = "error"
    try:
        db.execute(text("SELECT 1"))
        pg_status = "connected"
    except Exception as e:
        pg_status = f"unreachable: {str(e)}"

    mongo_status = "error"
    try:
        await mongo.command("ping")
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"unreachable: {str(e)}"

    return {
        "status": "online",
        "projet": settings.PROJECT_NAME,
        "env": settings.ENVIRONMENT,
        "databases": {
            "postgresql": pg_status,
            "mongodb": mongo_status
        }
    }