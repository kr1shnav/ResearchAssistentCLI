import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    if not model:
        raise ValueError("GEMINI_MODEL cannot be empty.")

    return Settings(api_key=api_key, model=model)