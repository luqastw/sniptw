from sqlalchemy import UUID, Column, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, relationship

from db.base import Base


class Click(Base):
    __tablename__ = "clicks"

    id = Column(UUID, primary_key=True, index=True, unique=True)
    link_id = Column(UUID, ForeignKey("links.id"))
    clicked_at = Column(DateTime(timezone=True), onupdate=func.now())
    country = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    referer = Column(String, nullable=True)
    ip_hash = Column(String, nullable=True)

    link: Mapped["Link"] = relationship(back_populates="clicks")
