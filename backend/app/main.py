from fastapi import FastAPI, Depends, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.dependencies import get_session
from backend.app.db.repositories.link_repository import LinkRepository
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.link_service import LinkService
from backend.app.api.v1.routes import auth, links, analytics

app = FastAPI(title="sniptw", version="0.1.0")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(links.router, prefix="/api/v1/links", tags=["Links"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


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
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    link_repository = LinkRepository(session)
    link_service = LinkService(link_repository)
    analytics_service = AnalyticsService(session)

    ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer", None)

    link = await link_service.redirect(slug, password=None)
    background_tasks.add_task(
        analytics_service.register_click, link.id, ip, user_agent, referer
    )
    return RedirectResponse(url=link.original_url, status_code=302)
