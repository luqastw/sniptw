from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.user import User
from backend.app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email):
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        users = result.scalar_one_or_none()
        return users

    async def get_by_username(self, username):
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        users = result.scalar_one_or_none()
        return users

    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
