"""Vercel deployment via Vercel CLI.

The pipeline uses `vercel --prod` to deploy from any branch — no git push,
no GitHub integration, no deploy branch. Works from wherever the pipeline
runs locally.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 300


def _get_vercel_token() -> str | None:
    """Read Vercel token from CLI auth file as fallback."""
    auth_path = Path.home() / ".local/share/com.vercel.cli/auth.json"
    try:
        d = json.loads(auth_path.read_text())
        return d.get("token", "")
    except Exception:
        return None


class Deployer:
    """Deploy the Next.js static site to Vercel via the Vercel CLI."""

    def __init__(
        self,
        *,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.timeout = timeout
        self._token: str | None = None

    @property
    def token(self) -> str:
        """Lazily load Vercel API token from env or CLI auth file."""
        if self._token:
            return self._token
        self._token = os.getenv("VERCEL_TOKEN") or os.getenv("VERCEL_API_TOKEN") or _get_vercel_token() or ""
        return self._token

    def deploy(self) -> str:
        """Deploy the web/ directory using Vercel CLI directly.

        Runs `vercel --prod` from the web/ directory — works from any branch,
        no GitHub connection needed.

        Returns:
            The live Vercel URL of the deployed edition.

        Raises:
            RuntimeError: If the deploy times out or fails.
        """
        load_dotenv()

        git_dir = Path(__file__).resolve().parents[2]
        edition_src = git_dir / "data" / "edition.json"
        web_data_dest = git_dir / "web" / "public" / "data" / "edition.json"

        if not edition_src.exists():
            raise RuntimeError(
                f"edition.json not found at {edition_src}. Run pipeline first."
            )

        web_data_dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy current pipeline output to web/public/data for deployment
        import shutil
        shutil.copy2(edition_src, web_data_dest)
        LOGGER.info("Copied edition.json to web/public/data/")

        # Deploy via Vercel CLI — runs from project root so Vercel resolves
        # the 'web' directory correctly relative to Vercel project settings.
        url = _deploy_via_vercel_cli(project_root=git_dir)
        LOGGER.info("Deployed to: %s", url)
        return url

    def deploy_and_return_url(self) -> str:
        """Alias for deploy() — kept for backwards compatibility."""
        return self.deploy()


def _deploy_via_vercel_cli(project_root: Path | None = None) -> str:
    """Deploy the web/ directory using Vercel CLI directly.

    Runs `vercel --prod` from the project root — Vercel CLI reads the
    project settings from .vercel/ in the project dir. Works from any branch.

    Args:
        project_root: Path to the news-to-me project root. Defaults to
                      the directory containing web/. If provided, Vercel
                      CLI will use the correct project root so the dashboard
                      setting (which expects the web/ subdir) is resolved
                        relative to this path.

    Returns:
        The Vercel deployment URL.

    Raises:
        RuntimeError: If the deploy fails.
    """
    import subprocess

    git_dir = Path(__file__).resolve().parents[2]
    # Vercel CLI should be run from the project root where .vercel/ lives,
    # so Vercel resolves 'web/' correctly relative to that root.
    project_root_dir = project_root or git_dir

    cmd = ["vercel", "--yes", "--prod"]
    result = subprocess.run(
        cmd,
        cwd=project_root_dir,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Vercel CLI deploy failed: {result.stderr}")

    # Parse URL from output
    for line in result.stdout.split("\n"):
        if "vercel.app" in line:
            url = line.strip().split(" ")[-1]
            return url

    raise RuntimeError(f"Could not parse Vercel URL from output: {result.stdout}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy News To Me to Vercel")
    parser.add_argument("--cli", action="store_true", help="Deploy using Vercel CLI directly")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        url = Deployer().deploy()
        print(f"Live URL: {url}")
    except RuntimeError as e:
        print(f"Deploy failed: {e}", file=__import__("sys").stderr)
        raise SystemExit(1)