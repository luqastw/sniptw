from sqlalchemy import (
    Column,
    UUID,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
    func,
)
from sqlalchemy.orm import Mapped, relationship

from backend.app.db.base import Base


class Link(Base):
    __tablename__ = "links"

    id = Column(UUID, primary_key=True, index=True, unique=True)
    slug = Column(String, index=True)
    original_url = Column(String(500), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"))
    click_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    password_hash = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="links")
    clicks: Mapped[list["Click"]] = relationship(back_populates="link")
