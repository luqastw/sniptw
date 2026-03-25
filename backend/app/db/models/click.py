from uuid import uuid4
from sqlalchemy import UUID, Column, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, relationship
from datetime import datetime, timezone


from backend.app.db.base import Base


class Click(Base):
    __tablename__ = "clicks"

    id = Column(UUID, primary_key=True, index=True, unique=True, default=uuid4)
    link_id = Column(UUID, ForeignKey("links.id"))
    clicked_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    country = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    referer = Column(String, nullable=True)
    ip_hash = Column(String, nullable=True)

    link: Mapped["Link"] = relationship(back_populates="clicks")
