# voiceagent/app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Azure Communication Services
    ACS_CONNECTION_STRING: str = ""

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"
    AZURE_OPENAI_GPT4O_DEPLOYMENT: str = "gpt-4o"
    AZURE_OPENAI_WHISPER_DEPLOYMENT: str = "whisper"
    AZURE_OPENAI_TTS_DEPLOYMENT: str = "tts"

    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING: str = ""

    # App Settings
    ENVIRONMENT: str = "dev"
    CALLBACK_BASE_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()