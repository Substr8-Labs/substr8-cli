"""
Substr8 Platform Shortcuts — Top-level commands that delegate to substr8-platform Makefile.

These are the most common operations every operator needs:
    substr8 doctor     → make doctor
    substr8 bootstrap  → make bootstrap
    substr8 up         → make up
    substr8 down       → make down
    substr8 restart    → make restart
    substr8 smoke      → make smoke
    substr8 test       → make test
    substr8 demo       → make demo
    substr8 clean      → make clean

The CLI does NOT reimplement any logic. It delegates entirely to the Makefile.
"""

import os
import subprocess
import sys

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

# Default platform root
DEFAULT_PLATFORM_ROOT = os.path.join(os.path.expanduser("~"), "workspace", "substr8-platform")


def _resolve_platform_root(root: str | None) -> str:
    """Resolve the substr8-platform directory."""
    platform_root = root or os.environ.get("SUBSTR8_PLATFORM_ROOT") or DEFAULT_PLATFORM_ROOT

    if not os.path.isdir(platform_root):
        console.print(f"[red]Error:[/red] substr8-platform not found at {platform_root}")
        console.print()
        console.print("Set [cyan]SUBSTR8_PLATFORM_ROOT[/cyan] or use [cyan]--root PATH[/cyan]")
        console.print(f"Or clone: [dim]gh repo clone Substr8-Labs/substr8-platform {platform_root}[/dim]")
        sys.exit(2)

    makefile = os.path.join(platform_root, "Makefile")
    if not os.path.isfile(makefile):
        console.print(f"[red]Error:[/red] No Makefile found at {platform_root}")
        console.print("Is this a valid substr8-platform directory?")
        sys.exit(2)

    return platform_root


def _run_make(platform_root: str, target: str, extra_args: list[str] | None = None,
              dry_run: bool = False, verbose: bool = False) -> int:
    """Run a make target in the platform directory."""
    cmd = ["make", "-C", platform_root, target]
    if extra_args:
        cmd.extend(extra_args)

    if dry_run:
        console.print(f"[dim]$ {' '.join(cmd)}[/dim]")
        return 0

    if verbose:
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")

    result = subprocess.run(cmd)
    return result.returncode


def _make_command(target: str, help_text: str):
    """Factory to create a click command that wraps a make target."""
    @click.command(name=target, help=help_text)
    @click.option("--root", type=click.Path(), help="Path to substr8-platform directory")
    @click.option("--dry-run", is_flag=True, help="Print command without executing")
    @click.option("--verbose", "-v", is_flag=True, help="Show command being run")
    def cmd(root, dry_run, verbose):
        platform_root = _resolve_platform_root(root)
        code = _run_make(platform_root, target, dry_run=dry_run, verbose=verbose)
        sys.exit(code)
    return cmd


# --- Top-level shortcut commands ---

doctor = _make_command("doctor", "Check dev environment prerequisites.")
bootstrap = _make_command("bootstrap", "First-time setup (env, deps, venvs).")
down = _make_command("down", "Stop all services.")
restart = _make_command("restart", "Restart core services.")
smoke = _make_command("smoke", "Platform health check.")
test_cmd = _make_command("test", "Run all tests.")
demo = _make_command("demo", "Seed NDIS demo data.")
clean = _make_command("clean", "Remove all containers, volumes, images, and data.")


@click.command(help="Start core services (Neo4j + ThreadHQ).")
@click.option("--root", type=click.Path(), help="Path to substr8-platform directory")
@click.option("--profile", type=click.Choice(["core", "proof", "memory", "runtime", "full", "demo"]),
              default=None, help="Compose profile to start")
@click.option("--dry-run", is_flag=True, help="Print command without executing")
@click.option("--verbose", "-v", is_flag=True, help="Show command being run")
def up(root, profile, dry_run, verbose):
    """Start platform services.

    Defaults to core profile (Neo4j + ThreadHQ).
    Use --profile for additional service groups.

    Examples:
        substr8 up
        substr8 up --profile memory
        substr8 up --profile full
    """
    platform_root = _resolve_platform_root(root)

    if profile == "full":
        target = "up-full"
    elif profile == "proof":
        target = "up-proof"
    elif profile == "memory":
        target = "up-memory"
    elif profile == "threadhq":
        target = "up-threadhq"
    else:
        target = "up"

    code = _run_make(platform_root, target, dry_run=dry_run, verbose=verbose)
    sys.exit(code)