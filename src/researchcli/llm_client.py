import time
from dataclasses import dataclass
from typing import Optional

from google import genai

from researchcli.config import load_settings


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str
    latency_seconds: float
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    finish_reason: Optional[str]


def generate_response(prompt: str) -> LLMResult:
    settings = load_settings()
    client = genai.Client(api_key=settings.api_key)

    try:
        start = time.perf_counter()

        response = client.models.generate_content(
            model=settings.model,
            contents=prompt,
        )

        latency = time.perf_counter() - start

        usage = response.usage_metadata
        candidates = response.candidates or []

        finish_reason = None
        if candidates and candidates[0].finish_reason is not None:
            finish_reason = str(candidates[0].finish_reason)

        if not response.text:
            raise RuntimeError(
                f"Gemini returned no text. Finish reason: {finish_reason}"
            )

        return LLMResult(
            text=response.text,
            model=getattr(response, "model_version", None)
            or settings.model,
            latency_seconds=latency,
            input_tokens=(
                getattr(usage, "prompt_token_count", None)
                if usage else None
            ),
            output_tokens=(
                getattr(usage, "candidates_token_count", None)
                if usage else None
            ),
            total_tokens=(
                getattr(usage, "total_token_count", None)
                if usage else None
            ),
            finish_reason=finish_reason,
        )

    finally:
        client.close()

def stream_response(prompt: str):
    """Yield Gemini response chunks as they arrive."""
    settings = load_settings()
    client = genai.Client(api_key=settings.api_key)

    try:
        stream = client.models.generate_content_stream(
            model=settings.model,
            contents=prompt,
        )

        yield from stream

    finally:
        client.close()
