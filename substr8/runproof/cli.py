"""
RunProof CLI — Proof service health, verification, and status.

Commands that talk to the RunProof API (default: Railway production).
Set RUNPROOF_API_URL to override.
"""

import os

import click
import httpx
from rich.console import Console

console = Console()

DEFAULT_API_URL = "https://runproof-api-production.up.railway.app"


def _api_url():
    return os.environ.get("RUNPROOF_API_URL", DEFAULT_API_URL)


def _get(path: str):
    url = f"{_api_url()}{path}"
    try:
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        console.print(f"[red]Error:[/red] Cannot reach RunProof API at {url}")
        raise SystemExit(1)
    except httpx.HTTPStatusError as e:
        detail = e.response.json() if e.response.headers.get("content-type", "").startswith("application/json") else e.response.text
        console.print(f"[red]Error:[/red] {e.response.status_code} — {detail}")
        raise SystemExit(1)


@click.group(name="runproof")
def runproof():
    """RunProof — proof service health, verification, and status."""
    pass


@runproof.command()
def health():
    """Check RunProof API health."""
    result = _get("/health")
    status = result.get("status", "unknown")
    db = result.get("database_type", "unknown")
    console.print(f"Status: [{'green' if status == 'healthy' else 'red'}]{status}[/]")
    console.print(f"Database: {db}")


@runproof.command("status")
@click.argument("run_id")
def run_status(run_id):
    """Check proof status for a run."""
    result = _get(f"/api/runs/{run_id}")
    proof_status = result.get("proof_status", "unknown")
    console.print(f"Run ID: [cyan]{run_id}[/cyan]")
    console.print(f"Proof Status: [{'green' if proof_status == 'complete' else 'yellow'}]{proof_status}[/]")
    if result.get("proof_id"):
        console.print(f"Proof ID: {result['proof_id']}")


@runproof.command("smoke")
def smoke():
    """Quick smoke test — health + connectivity."""
    result = _get("/health")
    status = result.get("status", "unknown")
    if status == "healthy":
        console.print("[green]✓[/green] RunProof API healthy")
    else:
        console.print(f"[red]✗[/red] RunProof API: {status}")