from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.app.db.models.link import Link
from backend.app.schemas.link import LinkCreate, LinkUpdate


class LinkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_slug(self, slug: str) -> Link | None:
        stmt = select(Link).where(Link.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, link_id: UUID) -> Link | None:
        stmt = select(Link).where(Link.id == link_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: UUID) -> list[Link]:
        stmt = select(Link).where(Link.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        data: LinkCreate,
        user_id: UUID,
        slug: str,
        expires_at: datetime | None,
        password_hash: str | None,
    ) -> Link:
        link = Link(
            user_id=user_id,
            original_url=str(data.original_url),
            slug=slug,
            expires_at=expires_at,
            password_hash=password_hash,
        )

        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def update(self, link: Link, data: LinkUpdate) -> Link:
        if data.original_url is not None:
            link.original_url = str(data.original_url)
        if data.is_active is not None:
            link.is_active = data.is_active

        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def delete(self, link: Link) -> None:
        link.is_active = False

        await self.session.commit()
        return None

    async def increment_click(self, link_id: UUID) -> None:
        stmt = (
            update(Link)
            .where(Link.id == link_id)
            .values(click_count=Link.click_count + 1)
        )

        await self.session.execute(stmt)
        await self.session.commit()
        return None
