from typing import Any, List, Optional

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from pydantic import EmailStr

from .base import Base, BaseFilter, BaseIdentifier, BaseList, BaseModel, BaseSaved


class User(Base):
    full_name: str = models.TextField()
    email: str = models.TextField()
    hashed_password: str = models.TextField()

    search_vector: Any = SearchVectorField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
        ]
        indexes = [
            models.Index(fields=["email"]),
            GinIndex(fields=["search_vector"]),
        ]


@receiver(post_save, sender=User, dispatch_uid="update_user_search_vector")
def update_user_search_vector(sender, instance, **kwargs):
    sender.objects.filter(id=instance.id).update(
        search_vector=SearchVector("full_name")
    )


class UserSaved(BaseSaved):
    full_name: str
    email: EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserIdentifier(BaseIdentifier):
    email: Optional[EmailStr] = None


class UserFilter(BaseFilter):
    search: Optional[str] = None


class UserList(BaseList):
    results: List[UserSaved]
