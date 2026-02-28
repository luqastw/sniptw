from fastapi import HTTPException, status

from backend.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.app.db.repositories.user_repository import UserRepository
from backend.app.schemas.user import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, user_data: UserCreate):
        user_email = await self.repository.get_by_email(user_data.email)
        user_username = await self.repository.get_by_username(user_data.username)
        if user_email is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use."
            )

        if user_username is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use.",
            )

        hashed_password = hash_password(user_data.password)

        user = await self.repository.create(user_data, hashed_password)
        return user

    async def login(self, email: str, password: str) -> dict:
        user = await self.repository.get_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
            )

        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
