import inspect
from types import FunctionType
from typing import Dict, Optional, Type

from django.core.exceptions import ObjectDoesNotExist
from fastapi import BackgroundTasks, Depends, Query, Request, Response
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, ValidationError  # noqa

from backend.models import User
from server.config import settings

cookie_sec = APIKeyCookie(name=settings.COOKIE_NAME, auto_error=False)


def get_current_user(
    cookie_value: Optional[str] = Depends(cookie_sec),
) -> Optional[User]:
    if cookie_value is None:
        return None

    # FIXME: You can't authenticate users by their ID, that isn't secure at all. This is just an example.
    try:
        return User.objects.get(id=cookie_value)
    except ObjectDoesNotExist:
        return None


class Server(BaseModel):
    request: Request
    response: Response
    background: BackgroundTasks
    user: Optional[User] = Depends(get_current_user)

    class Config:
        # Allows FastAPI to populate parameters automatically.
        arbitrary_types_allowed = True


def as_query(name: str, model_cls: Type[BaseModel]) -> FunctionType:
    """
    Takes a pydantic model class as input and creates a dependency with corresponding
    Query parameter definitions that can be used for GET requests.
    This will only work, if the fields defined in the input model can be turned into
    suitable query parameters. Otherwise fastapi will complain down the road.
    Arguments:
        name: Name for the dependency function.
        model_cls: A ``BaseModel`` inheriting model class as input.
    """
    names = []
    annotations: Dict[str, type] = {}
    defaults = []
    for field_model in model_cls.__fields__.values():
        field_info = field_model.field_info

        field_name = field_model.name
        names.append(field_name)
        annotations[field_name] = field_model.outer_type_
        defaults.append(Query(field_model.default, description=field_info.description))

    code = inspect.cleandoc(
        """
    def %s(%s):
        try:
            return %s(%s)
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                error['loc'] = ['query'] + list(error['loc'])
            raise HTTPException(422, detail=errors)
    """
        % (
            name,
            ", ".join(names),
            model_cls.__name__,
            ", ".join(["%s=%s" % (name, name) for name in names]),
        )
    )

    compiled = compile(code, "string", "exec")
    env = {model_cls.__name__: model_cls}
    env.update(**globals())
    func = FunctionType(compiled.co_consts[0], env, name)
    func.__annotations__ = annotations
    func.__defaults__ = (*defaults,)

    return func
