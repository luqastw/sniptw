import hashlib
from sqlalchemy import select
import user_agents

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from backend.app.db.models.link import Link
from backend.app.db.models.click import Click
from backend.app.schemas.analytics import LinkStats


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register_click(
        self, link_id: UUID, ip: str, user_agent_string: str, referer: str | None
    ) -> None:
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        ua = user_agents.parse(user_agent_string)

        try:
            async with AsyncClient() as client:
                response = await client.get(
                    f"http://ip-api.com/json/{ip}?fields=country"
                )
                country = response.json()["country"]
        except Exception:
            country = None

        if ua.is_bot:
            device_type = "bot"
        elif ua.is_mobile:
            device_type = "mobile"
        else:
            device_type = "desktop"

        click = Click(
            link_id=link_id,
            country=country,
            device_type=device_type,
            referer=referer,
            ip_hash=ip_hash,
        )

        self.session.add(click)
        await self.session.commit()

    async def get_stats(self, slug: str) -> LinkStats:
        stmt = select(Link).where(Link.slug == slug)
        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()

        if link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Link not found."
            )

        stmt = select(Click).where(Click.link_id == link.id)
        result = await self.session.execute(stmt)
        clicks = result.scalars().all()

        return LinkStats(
            slug=link.slug,
            original_url=link.original_url,
            total_clicks=link.click_count,
            clicks=clicks,
        )
