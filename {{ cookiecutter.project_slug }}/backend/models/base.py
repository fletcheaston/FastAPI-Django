import uuid
from datetime import datetime
from typing import Optional

from django.db import models
from humps import camelize
from pydantic import BaseModel as PydanticBase


class Base(models.Model):  # type: ignore
    id: uuid.UUID = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )

    created: datetime = models.DateTimeField(
        db_index=True,
        auto_now_add=True,
        editable=False,
    )

    updated: datetime = models.DateTimeField(
        db_index=True,
        auto_now=True,
        editable=False,
    )

    class Meta:
        abstract = True


class BaseModel(PydanticBase):
    # Standard config settings.
    class Config:
        # Camelize will give us camelCase field names for external usage (docs, client-side api, etc.)
        # while maintaining snake_case for internal usage.
        alias_generator = camelize

        # Allow internal usage of snake_case field names.
        allow_population_by_field_name = True

        # Extra whitespace? Gross.
        anystr_strip_whitespace = True

        # If not a standard or Pydantic type, just check `isinstance`.
        arbitrary_types_allowed = True

        # Allow FastAPI to auto-convert database objects to Pydantic objects.
        orm_mode = True

        # Private fields are cool.
        underscore_attrs_are_private = True

        # Just makes enum comparisons a bit cleaner.
        use_enum_values = True


class BaseSaved(BaseModel):
    # Every object from the database/cache/data-persistence-layer has these attributes.
    id: uuid.UUID
    created: datetime
    updated: datetime


class BaseIdentifier(BaseModel):
    # Potentially other ways to identify records, but the UUID is standard.
    id: Optional[uuid.UUID] = None


class BaseFilter(BaseModel):
    page: int = 1
    per_page: int = 100

    # These properties make Django pagination easier, using slice notation on querysets.
    @property
    def start(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def end(self) -> int:
        return self.page * self.per_page

    # TODO: Implement cursor based pagination.


class BaseList(BaseModel):
    total_result_count: int
