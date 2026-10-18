import time

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from google.genai import errors

from researchcli.config import load_settings
from researchcli.llm_client import stream_response

app = typer.Typer(
    name="research",
    help="A streaming CLI research assistant powered by Gemini.",
    no_args_is_help=True,
)

console = Console()


@app.callback()
def main() -> None:
    """ResearchCLI: a Gemini-powered research assistant."""
    pass

def display_api_error(exc: Exception) -> None:
    """Show actionable messages for common Gemini API errors."""
    if isinstance(exc, errors.APIError):
        code = exc.code

        if code == 400:
            message = "Invalid request. Check your prompt and model settings."
        elif code == 401:
            message = "Authentication failed. Check your Gemini API key."
        elif code == 403:
            message = "Access denied. Check your API key and permissions."
        elif code == 404:
            message = "Model or API endpoint not found. Check GEMINI_MODEL."
        elif code == 429:
            message = "Rate limit or quota exceeded. Check your Gemini usage limits."
        elif code in (500, 502, 503, 504):
            message = "Gemini is temporarily unavailable. Try again later."
        else:
            message = f"Gemini API returned HTTP {code}."

        console.print(f"[red]{message}[/red]")
        console.print(f"[dim]Details: {exc.message or str(exc)}[/dim]")
    else:
        console.print(
            f"[red]Request failed: {type(exc).__name__}: {exc}[/red]"
        )


@app.command()
def stream(
    question: str = typer.Argument(
        ...,
        help="The question you want to research.",
    ),
) -> None:
    """Stream Gemini responses and display readable Markdown."""
    start = time.perf_counter()
    first_text_time = None

    output_chunks = []
    input_tokens = None
    output_tokens = None
    total_tokens = None
    finish_reason = None
    model_used = None

    try:
        settings = load_settings()
        console.print(
            f"[bold cyan]ResearchCLI[/bold cyan] "
            f"[dim]({settings.model})[/dim]\n"
        )

        with console.status("[bold cyan]Researching..."):
            for chunk in stream_response(question):
                chunk_text = chunk.text

                if chunk_text:
                    if first_text_time is None:
                        first_text_time = time.perf_counter()

                    output_chunks.append(chunk_text)

                usage = getattr(chunk, "usage_metadata", None)

                if usage is not None:
                    input_tokens = getattr(
                        usage, "prompt_token_count", input_tokens
                    )
                    output_tokens = getattr(
                        usage, "candidates_token_count", output_tokens
                    )
                    total_tokens = getattr(
                        usage, "total_token_count", total_tokens
                    )

                candidates = getattr(chunk, "candidates", None) or []

                if candidates and candidates[0].finish_reason is not None:
                    finish_reason = str(candidates[0].finish_reason)

                model_used = (
                    getattr(chunk, "model_version", None) or model_used
                )

        elapsed = time.perf_counter() - start
        answer = "".join(output_chunks)

        if not answer.strip():
            console.print(
                "[yellow]Gemini returned no text.[/yellow]"
            )
            return

        console.print(
            Panel(
                Markdown(answer),
                title="Research Report",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        ttft = (
            first_text_time - start
            if first_text_time is not None
            else None
        )

        throughput = (
            output_tokens / elapsed
            if output_tokens is not None and elapsed > 0
            else None
        )

        metrics = Table(title="API Metrics")
        metrics.add_column("Metric", style="cyan")
        metrics.add_column("Value", style="green")

        metrics.add_row("Model", model_used or settings.model)
        metrics.add_row("Total elapsed", f"{elapsed:.2f} seconds")
        metrics.add_row(
            "Time to first text",
            f"{ttft:.2f} seconds" if ttft is not None else "Unavailable",
        )
        metrics.add_row(
            "Input tokens",
            str(input_tokens) if input_tokens is not None else "Unavailable",
        )
        metrics.add_row(
            "Output tokens",
            str(output_tokens)
            if output_tokens is not None else "Unavailable",
        )
        metrics.add_row(
            "Total tokens",
            str(total_tokens) if total_tokens is not None else "Unavailable",
        )
        metrics.add_row("Finish reason", finish_reason or "Unavailable")
        metrics.add_row(
            "Output tokens / second",
            f"{throughput:.2f}" if throughput is not None else "Unavailable",
        )

        console.print(metrics)

    except ValueError as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    except Exception as exc:
        display_api_error(exc)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
