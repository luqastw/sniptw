from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.dependencies import get_session, get_current_user
from backend.app.db.models.user import User
from backend.app.db.repositories.link_repository import LinkRepository
from backend.app.schemas.analytics import LinkStats
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.link_service import LinkService

router = APIRouter()


@router.get("/{slug}", response_model=LinkStats)
async def get_link_stats(
    slug: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LinkStats:
    link_repository = LinkRepository(session)
    link_service = LinkService(link_repository)
    analytics_service = AnalyticsService(session)

    link = await link_service.get_link_or_404(slug)
    if link.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return await analytics_service.get_stats(slug)
