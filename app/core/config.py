"""
Centralised application settings loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT / Auth ────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # ── Stripe (future) ──────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""

    # ── Cloudinary (Asset storage) ───────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # ── SMTP (Emails) ────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@cmo-ai.com"

    # ── Groq (LLM) ───────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 4096
    LLM_PROVIDER: str = "groq"  # "groq" or "openai"

    # ── OpenAI (optional) ────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── LangSmith / LangChain tracing (optional) ─────────────
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_PROJECT: str = "cmo-ai"

    # ── Cohere + Pinecone (content agent RAG) ────────────────
    COHERE_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "cmo-content-kb"

    # ── Runway (video + image agent) ─────────────────────────
    RUNWAY_API_KEY: str = ""
    RUNWAY_MODEL: str = "gen4.5"
    RUNWAY_RATIO: str = "1280:720"
    RUNWAY_DURATION: int = 5
    RUNWAY_IMAGE_MODEL: str = "gen4_image"

    # ── Image agent backend ──────────────────────────────────
    # auto = Runway when RUNWAY_API_KEY is set, else Pollinations when configured
    IMAGE_BACKEND: str = "auto"

    # ── Pollinations (optional image fallback) ─────────────
    POLLINATIONS_API_KEY: str = ""
    POLLINATIONS_MODEL: str = "flux"

    # ── Observability (optional) ─────────────────────────────
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"


settings = Settings()
