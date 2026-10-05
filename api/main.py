from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.dashboard import router as dashboard_router
from api.routes.cases import router as cases_router
from api.routes.evidence import router as evidence_router
from api.routes.network import router as network_router
from api.routes.analysis import router as analysis_router


app = FastAPI(
    title="Criminal Network Analyzer API",
    description="Backend API for the Criminal Network Analyzer",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

app.include_router(dashboard_router)
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(network_router)
app.include_router(analysis_router)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Criminal Network Analyzer API is running",
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }