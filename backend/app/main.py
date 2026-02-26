from fastapi import FastAPI

from backend.app.api.v1.routes import auth

app = FastAPI(title="sniptw", version="0.1.0")

app.include_router(auth.router, prefix="api/v1/auth", tags=["Authentication"])


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check.",
    description="Check if API is working.",
)
def health_check():
    return {"status": "online"}
