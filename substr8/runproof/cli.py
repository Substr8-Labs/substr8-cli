"""
RunProof CLI — Proof service, verification, and bundle management.

Service group commands (health, status, smoke) talk to the RunProof API.
Bundle commands (run, verify, export, badge) work locally.
"""

import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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


# ============= Service Group Commands =============

@click.group(name="runproof")
def runproof():
    """RunProof — proof service health, verification, and bundle management."""
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


# ============= Bundle Commands (local) =============

@runproof.command()
@click.argument("script", type=click.Path(exists=True))
@click.option("--framework", type=click.Choice(["auto", "langgraph", "pydantic-ai", "autogen"]),
              default="auto", help="Framework to use (auto-detect by default)")
@click.option("--local/--cloud", default=False, help="Use local MCP server (default: cloud)")
@click.option("--out", type=click.Path(), default="./runproofs", help="Output directory for RunProof")
@click.option("--label", multiple=True, help="Labels in k=v format")
@click.option("--mcp-url", envvar="SUBSTR8_MCP_URL", help="MCP server URL")
@click.option("--no-tarball", is_flag=True, help="Don't create .runproof.tgz archive")
def run(script: str, framework: str, local: bool, out: str, label: tuple, mcp_url: str, no_tarball: bool):
    """Run an agent script with Substr8 governance enabled."""
    script_path = Path(script).resolve()
    output_dir = Path(out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = f"run-{uuid.uuid4().hex[:6]}"
    started_at = datetime.now(timezone.utc)
    
    if framework == "auto":
        framework = detect_framework(script_path)
    
    if not mcp_url:
        mcp_url = "http://127.0.0.1:9988" if local else "https://mcp.substr8labs.com"
    
    console.print()
    console.print("[bold cyan]▶ Substr8 Governance: ACTIVE[/bold cyan]")
    console.print(f"  [dim]Run ID:[/dim]   {run_id}")
    console.print(f"  [dim]Mode:[/dim]     {'local' if local else 'cloud'}")
    console.print(f"  [dim]MCP:[/dim]      {mcp_url}")
    console.print(f"  [dim]Framework:[/dim] {framework}")
    console.print()
    
    env = os.environ.copy()
    env["SUBSTR8_RUN_ID"] = run_id
    env["SUBSTR8_MCP_URL"] = mcp_url
    env["SUBSTR8_GOVERNANCE"] = "active"
    
    exit_code = 0
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            capture_output=False,
        )
        exit_code = result.returncode
    except Exception as e:
        console.print(f"[red]Agent error:[/red] {e}")
        exit_code = 10
    
    ended_at = datetime.now(timezone.utc)
    
    try:
        from .bundle import create_runproof
        from .hash import sha256_str
        
        with open(script_path, 'r') as f:
            script_content = f.read()
        agent_hash = sha256_str(script_content)
        
        bundle = create_runproof(
            run_id=run_id,
            agent_ref=f"{framework}:{script_path.stem}",
            agent_hash=agent_hash,
            policy_hash=sha256_str("default-policy"),
            started_at=started_at,
            ended_at=ended_at,
            mcp_endpoint=mcp_url,
            model_provider="anthropic",
            model_name="claude-opus-4-5",
        )
        
        try:
            bundle = enrich_bundle_from_mcp(bundle, mcp_url, run_id)
        except Exception:
            pass
        
        result_path = bundle.save(output_dir, create_tarball=not no_tarball)
        
        if exit_code == 0:
            console.print("[bold green]Run completed ✓[/bold green]")
        else:
            console.print(f"[bold yellow]Run completed with exit code {exit_code}[/bold yellow]")
        
        console.print()
        console.print(f"[bold]RunProof:[/bold] {result_path}")
        console.print()
        
    except Exception as e:
        console.print(f"[red]✗ RunProof assembly failed:[/red] {e}")
        raise SystemExit(30)
    
    raise SystemExit(exit_code)


@runproof.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--strict", is_flag=True, help="Also verify signature")
def verify(path: str, as_json: bool, strict: bool):
    """Verify a RunProof bundle offline."""
    from .verify import verify_runproof
    
    result = verify_runproof(Path(path), strict=strict)
    
    if as_json:
        import json
        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.valid:
            console.print("[bold green]RunProof Verified ✓[/bold green]")
        else:
            console.print("[bold red]RunProof Verification FAILED ✗[/bold red]")
        
        console.print(f"[bold]Run:[/bold]        {result.run_id}")
        console.print(f"[bold]Agent:[/bold]      {result.agent_ref}")
        console.print(f"[bold]Root Hash:[/bold]  {'✓' if result.root_hash_valid else '✗'}")
        console.print(f"[bold]Ledger:[/bold]     {'✓' if result.ledger_valid else '✗'}")
        
        if result.errors:
            console.print("[bold red]Errors:[/bold red]")
            for error in result.errors:
                console.print(f"  • {error}")
    
    if not result.valid:
        raise SystemExit(1)


@runproof.command()
@click.argument("run_id")
@click.option("--out", type=click.Path(), default=".", help="Output directory")
@click.option("--format", "fmt", type=click.Choice(["tgz", "dir"]), default="tgz")
def export(run_id: str, out: str, fmt: str):
    """Export a RunProof from local cache."""
    import shutil
    
    cache_dir = Path.home() / ".substr8" / "runproof"
    local_path = cache_dir / run_id
    local_tgz = cache_dir / f"{run_id}.runproof.tgz"
    
    output_dir = Path(out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if local_tgz.exists():
        if fmt == "tgz":
            dest = output_dir / f"{run_id}.runproof.tgz"
            shutil.copy(local_tgz, dest)
            console.print(f"[green]✓[/green] Exported to {dest}")
        else:
            import tarfile
            dest = output_dir / run_id
            with tarfile.open(local_tgz, 'r:gz') as tar:
                tar.extractall(dest)
            console.print(f"[green]✓[/green] Exported to {dest}")
    elif local_path.exists():
        if fmt == "dir":
            dest = output_dir / run_id
            shutil.copytree(local_path, dest)
            console.print(f"[green]✓[/green] Exported to {dest}")
        else:
            import tarfile
            dest = output_dir / f"{run_id}.runproof.tgz"
            with tarfile.open(dest, 'w:gz') as tar:
                tar.add(local_path / "runproof", arcname="runproof")
            console.print(f"[green]✓[/green] Exported to {dest}")
    else:
        console.print(f"[red]✗[/red] RunProof '{run_id}' not found in local cache")
        raise SystemExit(1)


@runproof.command()
@click.argument("run_id_or_hash")
@click.option("--markdown/--html", default=True, help="Output format")
def badge(run_id_or_hash: str, markdown: bool):
    """Generate a badge snippet for README."""
    badge_url = f"https://verify.substr8.io/badge/{run_id_or_hash}.svg"
    verify_url = f"https://verify.substr8.io/run/{run_id_or_hash}"
    
    if markdown:
        console.print(f"[![Verified by Substr8]({badge_url})]({verify_url})")
    else:
        console.print(f'<a href="{verify_url}"><img src="{badge_url}" alt="Verified by Substr8" /></a>')


def detect_framework(script_path: Path) -> str:
    """Auto-detect the framework used in a script."""
    with open(script_path, 'r') as f:
        content = f.read()
    
    if "langgraph" in content.lower() or "from langgraph" in content:
        return "langgraph"
    elif "pydantic_ai" in content or "pydantic-ai" in content.lower():
        return "pydantic-ai"
    elif "autogen" in content.lower():
        return "autogen"
    else:
        return "unknown"


def enrich_bundle_from_mcp(bundle, mcp_url: str, run_id: str):
    """Try to fetch governance data from MCP server."""
    import requests
    
    try:
        response = requests.post(
            f"{mcp_url}/tools/audit.timeline",
            json={"run_id": run_id},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if "entries" in data:
                bundle.ledger_entries = data["entries"]
        
        response = requests.post(
            f"{mcp_url}/tools/cia.receipts",
            json={"run_id": run_id},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if "receipts" in data:
                bundle.cia_receipts = data["receipts"]
    except Exception:
        pass
    
    return bundle