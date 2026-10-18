import time

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from google.genai import errors

from researchcli.config import load_settings
from researchcli.llm_client import stream_response
from researchcli.prompts import build_research_prompt
from researchcli.storage import save_report

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
    """Display actionable Gemini API error messages."""
    if isinstance(exc, errors.APIError):
        code = exc.code

        messages = {
            400: "Invalid request. Check the prompt and model settings.",
            401: "Authentication failed. Check your Gemini API key.",
            403: "Access denied. Check your API key and permissions.",
            404: "Model or API endpoint not found. Check GEMINI_MODEL.",
            429: "Rate limit or quota exceeded. Check your Gemini usage.",
            500: "Gemini server error. Try again later.",
            502: "Gemini gateway error. Try again later.",
            503: "Gemini is temporarily unavailable.",
            504: "Gemini request timed out.",
        }

        console.print(
            f"[red]{messages.get(code, f'Gemini API error: HTTP {code}')}[/red]"
        )
        console.print(f"[dim]{exc.message or str(exc)}[/dim]")
    else:
        console.print(
            f"[red]Request failed: {type(exc).__name__}: {exc}[/red]"
        )


@app.command()
def stream(
    topic: str = typer.Argument(
        ...,
        help="The topic you want to research.",
    ),
) -> None:
    """Generate and save a structured research report."""
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
        prompt = build_research_prompt(topic)

        console.print(
            f"\n[bold cyan]ResearchCLI[/bold cyan] "
            f"[dim]({settings.model})[/dim]"
        )
        console.print(f"[bold]Topic:[/bold] {topic}\n")

        with console.status("[bold cyan]Researching topic..."):
            for chunk in stream_response(prompt):
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
        report = "".join(output_chunks).strip()

        if not report:
            console.print("[yellow]Gemini returned no report text.[/yellow]")
            raise typer.Exit(code=1)

        # Render the completed Markdown for readable terminal output.
        console.print(
            Panel(
                Markdown(report),
                title="Research Report",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        # Save the report locally.
        try:
            report_path = save_report(topic, report)
            console.print(
                f"\n[green]Report saved:[/green] {report_path.resolve()}"
            )
        except OSError as exc:
            console.print(
                f"\n[yellow]Could not save report:[/yellow] {exc}"
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
        metrics.add_row("Elapsed time", f"{elapsed:.2f} seconds")
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
        console.print(f"[red]Configuration or input error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    except typer.Exit:
        raise

    except Exception as exc:
        display_api_error(exc)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()