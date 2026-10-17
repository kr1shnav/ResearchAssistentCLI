import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from researchcli.config import load_settings
from researchcli.llm_client import generate_response

app = typer.Typer(
    name="research",
    help="A CLI research assistant powered by Gemini.",
    no_args_is_help=True,
)

console = Console()


@app.callback()
def main() -> None:
    """ResearchCLI: a Gemini-powered research assistant."""
    pass


@app.command()
def ask(
    question: str = typer.Argument(
        ...,
        help="The question you want to ask Gemini.",
    ),
) -> None:
    """Ask Gemini a question and inspect API usage."""
    try:
        settings = load_settings()
        console.print(f"[dim]Configured model: {settings.model}[/dim]")

        with console.status("[bold cyan]Calling Gemini..."):
            result = generate_response(question)

        console.print(
            Panel(
                result.text,
                title="ResearchCLI",
                border_style="cyan",
            )
        )

        table = Table(title="API Request Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Model returned", result.model)
        table.add_row(
            "Latency",
            f"{result.latency_seconds:.2f} seconds",
        )
        table.add_row(
            "Input tokens",
            str(result.input_tokens)
            if result.input_tokens is not None else "Unavailable",
        )
        table.add_row(
            "Output tokens",
            str(result.output_tokens)
            if result.output_tokens is not None else "Unavailable",
        )
        table.add_row(
            "Total tokens",
            str(result.total_tokens)
            if result.total_tokens is not None else "Unavailable",
        )
        table.add_row(
            "Finish reason",
            result.finish_reason or "Unavailable",
        )

        console.print(table)

    except ValueError as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    except Exception as exc:
        console.print(
            f"[red]Request failed:[/red] {type(exc).__name__}: {exc}"
        )
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()