import time

import typer
from rich.console import Console
from rich.panel import Panel

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
    """Ask Gemini a question."""
    try:
        settings = load_settings()
        console.print(f"[dim]Model: {settings.model}[/dim]")

        start = time.perf_counter()

        with console.status("[bold cyan]Thinking..."):
            answer = generate_response(question)

        elapsed = time.perf_counter() - start

        console.print(
            Panel(
                answer,
                title="ResearchCLI",
                border_style="cyan",
            )
        )
        console.print(f"[dim]Elapsed: {elapsed:.2f}s[/dim]")

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
