from django.apps import apps
from django.conf import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server import django_settings as server_settings
from server.urls import router

try:
    settings.configure(server_settings)
except RuntimeError:  # Avoid: "Settings already configured."
    pass

apps.populate(settings.INSTALLED_APPS)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
