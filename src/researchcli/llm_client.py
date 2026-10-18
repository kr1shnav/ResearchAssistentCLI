from collections.abc import Iterator

from google import genai
from google.genai import types

from researchcli.config import load_settings


def create_client() -> genai.Client:
    """Create a Gemini client with bounded retries."""
    settings = load_settings()

    return genai.Client(
        api_key=settings.api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=4,
                initial_delay=1.0,
                max_delay=8.0,
                exp_base=2.0,
                jitter=1.0,
                http_status_codes=[
                    408, 429, 500, 502, 503, 504
                ],
            )
        ),
    )


def stream_response(prompt: str) -> Iterator:
    """Yield response chunks from Gemini."""
    client = create_client()

    try:
        yield from client.models.generate_content_stream(
            model=load_settings().model,
            contents=prompt,
        )
    finally:
        client.close()
