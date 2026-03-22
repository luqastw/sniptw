from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.dependencies import get_current_user, get_session
from backend.app.db.models.user import User
from backend.app.db.repositories.link_repository import LinkRepository
from backend.app.services.link_service import LinkService
from backend.app.schemas.link import LinkCreate, LinkResponse, LinkUpdate

router = APIRouter()


@router.post("/", response_model=LinkResponse, summary="Create a link.")
async def create_link(
    data: LinkCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LinkResponse:
    repository = LinkRepository(session)
    service = LinkService(repository)
    return await service.create_link(data, current_user.id)


@router.get("/", summary="Lists all links.")
async def list_links(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[LinkResponse]:
    repository = LinkRepository(session)
    service = LinkService(repository)
    return await service.list_links(current_user.id)


@router.get("/{slug}", response_model=LinkResponse, summary="Get a link by slug.")
async def get_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> LinkResponse:
    repository = LinkRepository(session)
    service = LinkService(repository)
    return await service.get_link_or_404(slug)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    slug: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    repository = LinkRepository(session)
    service = LinkService(repository)
    return await service.delete_link(slug, current_user.id)


@router.patch("/{slug}", response_model=LinkResponse)
async def update(
    data: LinkUpdate,
    slug: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> LinkResponse:
    repository = LinkRepository(session)
    service = LinkService(repository)
    return await service.update_link(slug, current_user.id, data)
