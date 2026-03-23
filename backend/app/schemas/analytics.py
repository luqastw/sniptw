from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ClickResponse(BaseModel):
    id: UUID
    clicked_at: datetime
    country: str | None
    device_type: str | None
    referer: str | None

    model_config = ConfigDict(from_attributes=True)


class LinkStats(BaseModel):
    slug: str
    original_url: str
    total_clicks: int
    clicks: list[ClickResponse]
