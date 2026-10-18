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
    """Stream Gemini responses grounded with Google Search."""
    settings = load_settings()
    client = create_client()

    search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    config = types.GenerateContentConfig(
        tools=[search_tool],
    )

    try:
        yield from client.models.generate_content_stream(
            model=settings.model,
            contents=prompt,
            config=config,
        )
    finally:
        client.close()
