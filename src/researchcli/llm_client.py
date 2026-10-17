from google import genai

from researchcli.config import load_settings


def generate_response(prompt: str) -> str:
    settings = load_settings()

    with genai.Client(api_key=settings.api_key) as client:
        response = client.models.generate_content(
            model=settings.model,
            contents=prompt,
        )

    if not response.text:
        raise RuntimeError("The model returned no text response.")

    return response.text