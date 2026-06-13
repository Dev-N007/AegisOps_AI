import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database.session import engine, Base
from app.api.routes.incidents import router as incidents_router
from app.api.routes.agents import router as agents_router
from app.api.routes.simulation import router as simulation_router
from app.api.routes.analytics import router as analytics_router

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AegisOps AI API",
    description="Autonomous incident intelligence orchestrator powered by Gemini & LangGraph",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(incidents_router, prefix="/api/incidents", tags=["incidents"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(simulation_router, prefix="/api/simulate", tags=["simulation"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "AegisOps AI Backend",
        "engine": "LangGraph StateGraph",
        "model": "Gemini 2.5 Pro / Flash"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
