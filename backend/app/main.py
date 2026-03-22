from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.dependencies import get_session
from backend.app.db.repositories.link_repository import LinkRepository
from backend.app.services.link_service import LinkService
from backend.app.api.v1.routes import auth, links

app = FastAPI(title="sniptw", version="0.1.0")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(links.router, prefix="/api/v1/links", tags=["Links"])


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check.",
    description="Check if API is working.",
)
def health_check():
    return {"status": "online"}


@app.get("/{slug}")
async def redirect(
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    repository = LinkRepository(session)
    service = LinkService(repository)
    link = await service.redirect(slug, password=None)
    return RedirectResponse(url=link.original_url, status_code=302)
