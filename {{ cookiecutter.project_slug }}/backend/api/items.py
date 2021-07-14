import uuid
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status

from backend.models import Item, ItemCreate, ItemFilter, ItemList, ItemSaved
from backend.utils import Server, as_query

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=ItemSaved)
def create_item(
    new_item: ItemCreate,
    server: Server = Depends(),
) -> Any:
    if server.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User must be logged in to create an item.",
        )

    try:
        Item.objects.create(
            name=new_item.name,
            description=new_item.description,
            owner=server.user,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this item already exists.",
        )


@router.get("", response_model=ItemList)
def list_items(
    item_filter: ItemFilter = Depends(as_query("item_filter", ItemFilter)),
    server: Server = Depends(),
) -> Any:
    items = Item.objects.all()

    if item_filter.search:
        items = items.filter(search_vector=item_filter.search)

    if item_filter.owner_id:
        items = items.filter(owner_id=item_filter.owner_id)

    total_result_count = items.count()

    items = items[item_filter.start : item_filter.end]

    return {
        "total_result_count": total_result_count,
        "results": list(items),
    }


@router.get("/{id}", response_model=ItemSaved)
def retrieve_item(
    id: uuid.UUID,
    server: Server = Depends(),
) -> Any:
    try:
        return Item.objects.get(id=id)
    except ObjectDoesNotExist:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item with this ID does not exist.",
        )


@router.delete("/{id}", response_model=None)
def delete_item(
    id: uuid.UUID,
    server: Server = Depends(),
) -> Any:
    if server.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User must be logged in to delete an item.",
        )

    try:
        Item.objects.get(id=id, owner=server.user).delete()
    except ObjectDoesNotExist:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot delete an item unless it belongs to them.",
        )
