"""
Substr8 Platform group — Deeper orchestration commands beyond the top-level shortcuts.
"""

import os
import subprocess
import sys

import click
from rich.console import Console

console = Console()

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


@click.group(name="platform")
def platform():
    """Platform orchestration — deeper dev commands beyond the top-level shortcuts.

    For the most common operations, use the top-level shortcuts:
        substr8 doctor, substr8 up, substr8 down, substr8 smoke

    Use this group for less common operations:
        substr8 platform reset, substr8 platform clean, substr8 platform test
    """
    pass


@platform.command()
@click.option("--root", type=click.Path(), help="Path to substr8-platform directory")
@click.option("--dry-run", is_flag=True, help="Print command without executing")
@click.option("--verbose", "-v", is_flag=True, help="Show command being run")
def reset(root, dry_run, verbose):
    """Wipe data and restart core services."""
    platform_root = _resolve_platform_root(root)
    code = _run_make(platform_root, "reset", dry_run=dry_run, verbose=verbose)
    sys.exit(code)


@platform.command()
@click.option("--root", type=click.Path(), help="Path to substr8-platform directory")
@click.option("--dry-run", is_flag=True, help="Print command without executing")
@click.option("--verbose", "-v", is_flag=True, help="Show command being run")
def clean(root, dry_run, verbose):
    """Remove all containers, volumes, images, and data."""
    platform_root = _resolve_platform_root(root)
    code = _run_make(platform_root, "clean", dry_run=dry_run, verbose=verbose)
    sys.exit(code)


@platform.command("test")
@click.option("--root", type=click.Path(), help="Path to substr8-platform directory")
@click.option("--dry-run", is_flag=True, help="Print command without executing")
@click.option("--verbose", "-v", is_flag=True, help="Show command being run")
def platform_test(root, dry_run, verbose):
    """Run all platform tests."""
    platform_root = _resolve_platform_root(root)
    code = _run_make(platform_root, "test", dry_run=dry_run, verbose=verbose)
    sys.exit(code)


@platform.command()
@click.option("--root", type=click.Path(), help="Path to substr8-platform directory")
@click.option("--dry-run", is_flag=True, help="Print command without executing")
@click.option("--verbose", "-v", is_flag=True, help="Show command being run")
def demo(root, dry_run, verbose):
    """Seed NDIS demo data."""
    platform_root = _resolve_platform_root(root)
    code = _run_make(platform_root, "demo", dry_run=dry_run, verbose=verbose)
    sys.exit(code)