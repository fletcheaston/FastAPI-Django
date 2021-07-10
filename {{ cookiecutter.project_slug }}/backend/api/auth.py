import uuid
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from fastapi import APIRouter, Depends, HTTPException, status

from backend.models import User, UserLogin, UserSaved
from backend.utils import Server, as_query, get_password_hash, verify_password
from server.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("", response_model=UserSaved)
def login(
    user_login: UserLogin,
    server: Server = Depends(),
) -> Any:
    if server.user is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is already logged in.",
        )

    try:
        user = User.objects.get(email=user_login.email)

        assert verify_password(
            plain_password=user_login.password, hashed_password=user.hashed_password
        )

        # FIXME: THIS IS NOT SECURE AT ALL.
        # You'll really want to create a session, use a JWT, or something else.
        # This just creates a cookie with the user's ID. Not secure at all.
        server.response.set_cookie(key=settings.COOKIE_NAME, value=user.id)

        return user

    except (ObjectDoesNotExist, AssertionError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials.",
        )


@router.delete("", response_model=None)
def logout(
    server: Server = Depends(),
) -> Any:
    if server.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not logged in.",
        )

    server.response.delete_cookie(key=settings.COOKIE_NAME)
