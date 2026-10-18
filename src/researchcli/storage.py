from datetime import datetime
from pathlib import Path
import re


REPORTS_DIR = Path("research_reports")


def save_report(topic: str, content: str) -> Path:
    """Save a completed research report as a Markdown file."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
    slug = slug[:60] or "research"

    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    report_path = REPORTS_DIR / f"{timestamp}-{slug}.md"

    report = (
        f"<!-- Topic: {topic} -->\n"
        f"<!-- Created: {datetime.now().astimezone().isoformat()} -->\n\n"
        f"{content.strip()}\n"
    )

    report_path.write_text(report, encoding="utf-8")
    return report_path
