import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from pydantic import root_validator

from .base import Base, BaseFilter, BaseIdentifier, BaseList, BaseModel, BaseSaved

if TYPE_CHECKING:
    from .users import User  # noqa: F401


class Item(Base):
    name: str = models.TextField()
    description: str = models.TextField()
    owner: "User" = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
    )

    search_vector: Any = SearchVectorField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "owner"], name="unique_owner_and_name"
            ),
        ]
        indexes = [
            models.Index(fields=["name", "owner"]),
            GinIndex(fields=["search_vector"]),
        ]

    def save(self, *args, **kwargs):
        self.search_vector = SearchVector("name", weight="A") + SearchVector(
            "description", weight="B"
        )
        super().save(*args, **kwargs)


class ItemSaved(BaseSaved):
    name: str
    description: str
    owner_id: uuid.UUID


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemIdentifier(BaseIdentifier):
    name: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None

    @root_validator()  # TODO: This is all business logic, do I really want business logic here?
    def check_for_id_xor_owner_and_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # If ID is not None, ensure owner_id and name are None.
        if values.get("id") is not None:
            assert values.get("name") is None
            assert values.get("owner_id") is None

        else:
            assert values.get("name") is not None
            assert values.get("owner_id") is not None

        return values


class ItemFilter(BaseFilter):
    search: Optional[str] = None
    owner_id: Optional[uuid.UUID] = None


class ItemList(BaseList):
    results: List[ItemSaved]
