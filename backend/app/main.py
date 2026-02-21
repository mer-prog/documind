from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analytics, auth, chat, conversations, documents

app = FastAPI(title="DocuMind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/mode")
async def get_mode():
    is_live = bool(settings.OPENAI_API_KEY)
    return {
        "mode": "live" if is_live else "demo",
        "model": settings.CHAT_MODEL if is_live else None,
    }
