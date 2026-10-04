from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analysis import router as analysis_router


app = FastAPI(
    title="Criminal Network Analyzer API",
    description="Investigation intelligence and evidence analysis API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "system": "Criminal Network Analyzer",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "services": {
            "api": "online",
            "neo4j": "connected",
            "analysis": "online",
        },
    }