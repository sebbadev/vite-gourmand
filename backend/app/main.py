from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vite & Gourmand API",
    description="API RESTful traiteur événementiel (FastAPI, PostgreSQL, MongoDB)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour autoriser le front-end Angular
origins = [
    "http://localhost:4200",  # Serveur de dev Angular
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "online",
        "projet": "Vite & Gourmand",
        "version": "1.0.0",
        "env": "development"
    }