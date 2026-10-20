# ResearchCLI

**An AI-powered research assistant built for the terminal.**

ResearchCLI is a Python-based CLI application that helps users research topics, generate AI-powered explanations, retrieve web-grounded information, and produce structured Markdown reports — all without leaving the terminal.

Powered by Google's Gemini API, ResearchCLI combines streaming responses, web research, source attribution, performance metrics, and report generation in a lightweight command-line workflow.

## Features

- **AI-Powered Research:** Generate detailed responses to research questions using Google Gemini.
- **Streaming Responses:** Display generated content progressively for a responsive research experience.
- **Web-Grounded Research:** Use Google Search grounding to incorporate relevant web information into research responses.
- **Source Attribution:** Collect available source URLs from grounding metadata to support further investigation.
- **Readable Terminal Output:** Present responses in a clean, structured Markdown format.
- **Markdown Reports:** Save research results as Markdown documents for future reference.
- **Token Usage Tracking:** Capture available input and output token usage information.
- **Latency Measurement:** Measure request duration to understand response performance.
- **Response Metadata:** Inspect available model and API response information.
- **Error Handling:** Handle API failures and transient errors gracefully.
- **Retry Support:** Retry eligible failed requests where appropriate.
- **Secure Configuration:** Load API credentials from environment variables rather than hardcoding secrets.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Google Gemini API | AI-generated research |
| `google-genai` | Gemini API integration |
| Typer | Command-line interface |
| Rich | Terminal formatting and presentation |
| `python-dotenv` | Environment variable management |
| Markdown | Research report storage |

## Installation

### Prerequisites

- Python 3.10 or newer
- A Google AI Studio API key
- Git

### 1. Clone the repository

```bash
git clone https://github.com/kr1shnav/ResearchCLI.git
cd ResearchCLI
```

Replace the URL if your repository uses a different name.

### 2. Create a virtual environment

**Windows — PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If the project has an installable `pyproject.toml` configuration:

```bash
python -m pip install -e .
```

Otherwise, install the required packages directly:

```bash
python -m pip install google-genai python-dotenv typer rich
```

### 4. Configure your API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-flash-latest
```

Obtain your API key from [Google AI Studio](https://aistudio.google.com/).

Ensure `.env` is listed in `.gitignore` and never commit your API key to GitHub.

## Usage

ResearchCLI uses a streaming-first workflow to deliver responses progressively while preserving readable terminal output.

### Run a research query

```bash
research stream "Explain retrieval-augmented generation"
```

Example research topics:

```bash
research stream "Compare vector databases for AI applications"
```

```bash
research stream "Explain transformer architecture in detail"
```

```bash
research stream "Analyse the applications of AI in climate prediction"
```

The `research` command assumes that the CLI entry point is installed and configured in the project. If it is not available, use the invocation method defined by your repository.

## How It Works

ResearchCLI processes a research request through the following stages:

1. **Query input:** Accept a research question from the terminal.
2. **Configuration:** Load API credentials and model settings from the environment.
3. **Model invocation:** Send the query to the configured Gemini model.
4. **Response streaming:** Receive generated content incrementally.
5. **Web grounding:** Incorporate Google Search results when grounding is enabled for the request.
6. **Output formatting:** Present the generated response in a readable structure.
7. **Source collection:** Extract available source references from the response metadata.
8. **Performance tracking:** Record request latency and available token usage.
9. **Report generation:** Store research results in Markdown format when report saving is invoked.

## Architecture

ResearchCLI separates the command-line interface, model integration, response presentation, and research output into logical responsibilities.

```text
                 ┌──────────────────────┐
                 │     User Query       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     CLI Interface    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Gemini API Client   │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴───────────┐
                 ▼                      ▼
       ┌──────────────────┐   ┌──────────────────┐
       │ Response Stream  │   │  Web Grounding   │
       └─────────┬────────┘   └─────────┬────────┘
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Formatting & Metrics │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Markdown Research    │
                 │ Report & Sources     │
                 └──────────────────────┘
```

The diagram represents the logical workflow; individual modules may differ depending on the implementation.

## Performance and Usage Metrics

ResearchCLI captures available metadata to help users understand the cost and responsiveness of model requests.

| Metric | Description |
|---|---|
| Input tokens | Tokens consumed by the input, when reported |
| Output tokens | Tokens generated by the model, when reported |
| Total tokens | Total token usage, when available |
| Latency | Elapsed time for the measured request |
| Model metadata | Information about the model and response |
| Request status | Success or failure of the request |

Token counts and other metadata depend on what the Gemini API returns for a particular request. Latency measurements should be interpreted according to the application's measurement boundaries.

## Error Handling and Reliability

ResearchCLI incorporates error-handling practices designed to make API interactions more reliable.

- Handles API errors without exposing credentials.
- Supports retries for eligible transient failures.
- Separates configuration problems from request failures where possible.
- Reports failures so users can diagnose unsuccessful requests.
- Avoids treating unsuccessful API calls as successful research results.

Retry policies should account for rate limits and transient server failures to avoid unnecessary repeated requests.

## Research Reports

Research results can be stored in Markdown, providing a portable format that works with GitHub, VS Code, Obsidian, and other Markdown-compatible tools.

A report can contain:

- Research question
- Generated explanation
- Structured sections and lists
- Source URLs available from grounding metadata
- Request metadata, when included by the application

Markdown reports make research easier to review, edit, share, and version-control.

## Project Structure

An illustrative repository layout is shown below. Keep the actual file names aligned with your implementation.

```text
ResearchCLI/
├── src/
│   └── researchcli/
│       ├── __init__.py
│       └── cli.py
├── reports/
├── .env
├── .gitignore
├── pyproject.toml
└── README.md
```

- `cli.py` — Command-line entry point and workflow coordination.
- `reports/` — Destination for saved research reports, if configured.
- `.env` — Local API configuration.
- `.gitignore` — Excludes credentials, virtual environments, and generated files as appropriate.
- `pyproject.toml` — Package configuration and CLI entry-point definitions.

## Security

ResearchCLI follows basic security practices for API-driven applications:

- Store credentials in environment variables.
- Exclude `.env` from version control.
- Avoid logging API keys and other secrets.
- Use supported API access and model configurations.
- Review research output and source links before relying on generated claims.

## Limitations

ResearchCLI relies on the configured Gemini model and the availability of its API services. Generated responses may contain errors, and web-grounded responses are not automatically guaranteed to be fully accurate or comprehensively cited. Token usage and metadata may also vary between requests.

**ResearchCLI brings AI-assisted research, streaming generation, web grounding, and structured reporting into a single terminal-based workflow.**