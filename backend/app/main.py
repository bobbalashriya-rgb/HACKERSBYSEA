from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.database import init_db

app = FastAPI(
    title="Finolitics AI API",
    description="Backend API for the Finolitics investment research assistant MVP.",
    version="0.1.0"
)

# Initialize database and seed defaults on startup
init_db()

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api prefix
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Finolitics AI API is running. Access /docs for Swagger UI."}

