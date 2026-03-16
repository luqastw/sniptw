from uuid import UUID
from pydantic import BaseModel, AnyHttpUrl, ConfigDict
from datetime import datetime


class LinkCreate(BaseModel):
    original_url: AnyHttpUrl
    slug: str | None = None
    expires_in_days: int | None = None
    password: str | None = None


class LinkResponse(BaseModel):
    id: UUID
    slug: str
    original_url: str
    click_count: int
    is_active: bool
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LinkAccess(BaseModel):
    password: str


class LinkUpdate(BaseModel):
    original_url: str | None = None
    is_active: bool | None = None
