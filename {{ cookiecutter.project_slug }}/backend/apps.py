from django.apps import AppConfig


class BackendConfig(AppConfig):  # type: ignore
    name = "backend"

    def ready(self) -> None:
        from server.urls import router as server_router

        from .api import router as app_router

        server_router.include_router(app_router)
