from sqlalchemy import Column, UUID, DateTime, String, Boolean, func
from sqlalchemy.orm import Mapped, relationship

from backend.app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, unique=True, index=True)
    email = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    links: Mapped[list["Link"]] = relationship(back_populates="user")
