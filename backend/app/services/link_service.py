from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import HTTPException, status
from secrets import token_urlsafe

from backend.app.db.repositories.link_repository import LinkRepository
from backend.app.schemas.link import LinkCreate, LinkUpdate
from backend.app.core.security import hash_password, verify_password
from backend.app.db.models.link import Link


class LinkService:
    def __init__(self, repository: LinkRepository) -> None:
        self.repository = repository

    async def create_link(self, data: LinkCreate, user_id: UUID) -> Link:
        if data.slug is not None:
            existing_link = await self.repository.get_by_slug(data.slug)
            if existing_link:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Already exists a link with this slug.",
                )

        slug = data.slug or token_urlsafe(4)
        expires_at = None
        password_hash = None

        if data.expires_in_days is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(
                days=data.expires_in_days
            )

        if data.password is not None:
            password_hash = hash_password(data.password)

        link = await self.repository.create(
            data, user_id, slug, expires_at, password_hash
        )
        return link

    async def get_link_or_404(self, slug: str) -> Link:
        link = await self.repository.get_by_slug(slug)

        if link is None or link.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Link not found."
            )

        return link

    async def redirect(self, slug: str, password: str | None) -> Link:
        link = await self.get_link_or_404(slug)

        if link.expires_at is not None and link.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="Expired link."
            )

        if link.password_hash:
            if password is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="This link requires a password.",
                )
            if not verify_password(password, link.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password.",
                )

        await self.repository.increment_click(link.id)
        return link

    async def list_links(self, user_id: UUID) -> list[Link]:
        return await self.repository.get_all_by_user(user_id)

    async def delete_link(self, slug: str, user_id: UUID) -> None:
        link = await self.get_link_or_404(slug)
        if link.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Restricted action."
            )

        await self.repository.delete(link)

    async def update_link(self, slug: str, user_id: UUID, data: LinkUpdate) -> Link:
        link = await self.get_link_or_404(slug)
        if link.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Restricted action."
            )
        return await self.repository.update(link, data)
