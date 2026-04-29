"""
SpecHQ CLI — Spec capture, harness compilation, and package generation.

Commands that talk to the SpecHQ API server (default: http://localhost:3456).
Set SPECHQ_API_URL to override.
"""

import os

import click
import httpx
from rich.console import Console

console = Console()

DEFAULT_API_URL = "http://localhost:3456"


def _api_url():
    return os.environ.get("SPECHQ_API_URL", DEFAULT_API_URL)


def _get(path: str, base_url: str | None = None):
    url = f"{base_url or _api_url()}{path}"
    try:
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        console.print(f"[red]Error:[/red] Cannot reach SpecHQ API at {url}")
        console.print("Is the API server running? Try: [dim]substr8 spechq dev[/dim]")
        raise SystemExit(1)


def _post(path: str, body: dict, base_url: str | None = None):
    url = f"{base_url or _api_url()}{path}"
    try:
        r = httpx.post(url, json=body, timeout=120)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        console.print(f"[red]Error:[/red] Cannot reach SpecHQ API at {url}")
        raise SystemExit(1)
    except httpx.HTTPStatusError as e:
        detail = e.response.json() if e.response.headers.get("content-type", "").startswith("application/json") else e.response.text
        console.print(f"[red]Error:[/red] {e.response.status_code} — {detail}")
        raise SystemExit(1)


@click.group(name="spechq")
def spechq():
    """SpecHQ — spec capture, harness compilation, and package generation."""
    pass


@spechq.command()
def health():
    """Check SpecHQ API health."""
    result = _get("/api/health")
    console.print(f"Status: [green]{result.get('status', 'unknown')}[/green]")
    console.print(f"Timestamp: {result.get('timestamp', 'n/a')}")


@spechq.command()
@click.argument("project_id")
@click.argument("spec_id")
def compile(project_id, spec_id):
    """Compile a spec into a HarnessSpec JSON."""
    result = _post("/api/harness/compile", {"projectId": project_id, "specId": spec_id})
    console.print(f"Export ID: [cyan]{result.get('id', 'n/a')}[/cyan]")
    console.print(f"Status: [green]{result.get('status', 'n/a')}[/green]")


@spechq.command("generate-package")
@click.argument("export_id")
def generate_package(export_id):
    """Generate a harness-core package from a compiled export."""
    result = _post("/api/harness/generate-package", {"exportId": export_id})
    console.print(f"Export ID: [cyan]{result.get('id', 'n/a')}[/cyan]")
    console.print(f"Status: [green]{result.get('status', 'n/a')}[/green]")


@spechq.command("validate-package")
@click.argument("export_id")
def validate_package(export_id):
    """Validate a generated harness package."""
    result = _post("/api/harness/validate-package", {"exportId": export_id})
    console.print(f"Valid: [{'green' if result.get('valid') else 'red'}]{result.get('valid')}[/]")
    if result.get("packageId"):
        console.print(f"Package ID: [cyan]{result['packageId']}[/cyan]")
    for err in result.get("errors", []):
        console.print(f"  [red]Error:[/red] {err}")
    for warn in result.get("warnings", []):
        console.print(f"  [yellow]Warning:[/yellow] {warn}")


@spechq.command("run-package")
@click.argument("export_id")
def run_package(export_id):
    """Run a validated harness package."""
    result = _post("/api/harness/run-package", {"exportId": export_id})
    success = result.get("success", False)
    console.print(f"Success: [{'green' if success else 'red'}]{success}[/]")
    if result.get("runId"):
        console.print(f"Run ID: [cyan]{result['runId']}[/cyan]")
    if result.get("threadhqUrl"):
        console.print(f"ThreadHQ: [link={result['threadhqUrl']}]{result['threadhqUrl']}[/link]")


@spechq.command("exports")
@click.argument("project_id")
def list_exports(project_id):
    """List harness exports for a project."""
    result = _get(f"/api/harness/exports/{project_id}")
    if not result:
        console.print("[dim]No exports found.[/dim]")
        return
    for exp in result:
        console.print(f"  {exp.get('id', 'n/a')}  [{exp.get('status', 'n/a')}]  {exp.get('createdAt', 'n/a')}")


@spechq.command("threadhq-link")
@click.argument("run_id")
def threadhq_link(run_id):
    """Get ThreadHQ URL for a run."""
    result = _get(f"/api/harness/threadhq-link/{run_id}")
    console.print(f"ThreadHQ: [link={result.get('threadhqUrl', '')}]{result.get('threadhqUrl', 'n/a')}[/link]")