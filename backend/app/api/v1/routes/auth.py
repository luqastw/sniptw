from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.repositories.user_repository import UserRepository
from backend.app.db.session import get_session
from backend.app.schemas.user import Token, UserCreate, UserResponse
from backend.app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with the provided information.",
)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserResponse:
    repository = UserRepository(session)
    service = AuthService(repository)
    user = await service.register(user_data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login an existing user.",
    description="Authenticate with email and password to receive an access token.",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> Token:
    repository = UserRepository(session)
    service = AuthService(repository)
    return await service.login(form_data.username, form_data.password)
