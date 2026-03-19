from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_session
from jose import jwt, JWTError

from backend.app.core.config import settings
from backend.app.db.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    try:
        repository = UserRepository(session)
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_email: str = payload.get("sub")

        user = await repository.get_by_email(user_email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
