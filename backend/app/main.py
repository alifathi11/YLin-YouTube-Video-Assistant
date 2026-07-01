from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes_health import router as health_router
from app.api.routes_videos import router as videos_router
from app.api.routes_chat import router as chat_router 

app = FastAPI(
	title=settings.app_name,
	version="0.1.0"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(videos_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)