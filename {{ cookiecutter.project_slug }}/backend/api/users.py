import uuid
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status

from backend.models import User, UserCreate, UserFilter, UserList, UserSaved
from backend.utils import Server, as_query, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserSaved)
def create_user(
    new_user: UserCreate,
    server: Server = Depends(),
) -> Any:
    if server.user is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is already logged in.",
        )

    try:
        return User.objects.create(
            full_name=new_user.full_name,
            email=new_user.email,
            hashed_password=get_password_hash(new_user.password),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )


@router.get("", response_model=UserList)
def list_users(
    user_filter: UserFilter = Depends(as_query("user_filter", UserFilter)),
    server: Server = Depends(),
) -> Any:
    users = User.objects.all()

    if user_filter.search:
        users = users.filter(search_vector=user_filter.search)

    total_result_count = users.count()

    users = users[user_filter.start : user_filter.end]

    return {
        "total_result_count": total_result_count,
        "results": list(users),
    }


@router.get("/{id}", response_model=UserSaved)
def retrieve_user(
    id: uuid.UUID,
    server: Server = Depends(),
) -> Any:
    try:
        return User.objects.get(id=id)
    except ObjectDoesNotExist:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this ID does not exist.",
        )


@router.delete("", response_model=None)
def delete_my_user(
    server: Server = Depends(),
) -> Any:
    if server.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User must be logged in to delete their account.",
        )

    server.user.delete()
