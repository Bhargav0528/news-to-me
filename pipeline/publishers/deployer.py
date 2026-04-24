"""Vercel deployment via git push to deploy branch.

Option B from SCRUM-40: pipeline commits web/public/data/edition.json
to a deploy branch and pushes. Vercel auto-deploys on push. Pipeline
waits for deploy completion and returns the live URL.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)

# Vercel project identifiers — hardcoded after `vercel project rename web news-to-me`
DEFAULT_ORG_ID = "team_vYrVM5DqTxvFtTQPkK1zKZmG"
DEFAULT_PROJECT_ID = "prj_zMCAGbKtHcSfVkXeuVwpBgV8VKSt"
DEFAULT_DEPLOY_BRANCH = "deploy"
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
    """Deploy the Next.js static site to Vercel by pushing edition data to git."""

    def __init__(
        self,
        *,
        org_id: str = DEFAULT_ORG_ID,
        project_id: str = DEFAULT_PROJECT_ID,
        deploy_branch: str = DEFAULT_DEPLOY_BRANCH,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.deploy_branch = deploy_branch
        self.timeout = timeout
        self._token: str | None = None

    @property
    def token(self) -> str:
        """Lazily load Vercel API token from env or CLI auth file."""
        if self._token:
            return self._token
        self._token = (
            os.getenv("VERCEL_TOKEN")
            or os.getenv("VERCEL_API_TOKEN")
            or _get_vercel_token()
            or ""
        )
        return self._token

    def deploy(self) -> str:
        """Push edition.json to the deploy branch and wait for Vercel to finish deploying.

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

        # Push to deploy branch
        self._git_push(git_dir, web_data_dest)

        # Wait for Vercel deployment to complete
        url = self._wait_for_deployment()
        LOGGER.info("Deployed to: %s", url)
        return url

    def _git_push(self, git_dir: Path, data_file: Path) -> None:
        """Stage web/public/data/edition.json, commit, and push to deploy branch."""
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "News To Me Pipeline"
        env["GIT_AUTHOR_EMAIL"] = "pipeline@newstome.local"
        env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
        env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]

        # Ensure deploy branch exists and is at this commit
        subprocess.run(
            ["git", "fetch", "origin", self.deploy_branch],
            cwd=git_dir,
            capture_output=True,
            text=True,
        )
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/heads/{self.deploy_branch}"],
            cwd=git_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "checkout", "-b", self.deploy_branch],
                cwd=git_dir,
                check=True,
                env=env,
            )
        else:
            subprocess.run(
                ["git", "checkout", self.deploy_branch],
                cwd=git_dir,
                check=True,
                env=env,
            )

        # Reset deploy branch to match main's current state (main has the latest code)
        # This ensures Vercel builds from main's content, not an old deploy branch state
        subprocess.run(
            ["git", "reset", "--hard", "origin/main"],
            cwd=git_dir,
            check=True,
            env=env,
        )

        # Stage the edition.json
        data_file = web_dir / "public" / "data" / "edition.json"
        subprocess.run(
            ["git", "add", str(data_file.relative_to(git_dir))],
            cwd=git_dir,
            check=True,
        )

        # Check if there's anything to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=git_dir,
            capture_output=True,
            text=True,
        )
        if not status.stdout.strip():
            LOGGER.info("edition.json unchanged — pushing main state as-is")
        else:
            message = f"Auto-deploy: update edition.json {time.strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=git_dir,
                check=True,
                env=env,
            )

        # Force push to deploy branch — this is the Vercel trigger
        subprocess.run(
            ["git", "push", "-f", "-u", "origin", self.deploy_branch],
            cwd=git_dir,
            check=True,
            env=env,
        )
        LOGGER.info("Pushed to origin/%s", self.deploy_branch)

    def _wait_for_deployment(self) -> str:
        """Poll Vercel API for the most recent deployment and wait for READY.

        Returns:
            The live Vercel URL of the deployed edition.

        Raises:
            RuntimeError: If the deploy times out or fails.
        """
        import requests

        token = self.token
        if not token:
            raise RuntimeError(
                "VERCEL_TOKEN env var is required to poll deployment status. "
                "Set it in .env or environment."
            )

        headers = {"Authorization": f"Bearer {token}"}
        base_url = "https://api.vercel.com/v6"
        deadline = time.time() + self.timeout

        while time.time() < deadline:
            resp = requests.get(
                f"{base_url}/deployments",
                headers=headers,
                params={"projectId": self.project_id, "limit": 3},
                timeout=30,
            )
            resp.raise_for_status()
            deployments = resp.json().get("deployments", [])

            for dep in deployments:
                meta = dep.get("meta", {})
                git_ref = meta.get("githubCommitRef", "") or meta.get("gitCommitRef", "")

                # Skip if not a deploy-branch push or not ready yet
                if git_ref != self.deploy_branch:
                    continue

                state = dep.get("state") or dep.get("status", "")
                uid = dep.get("uid", "")
                LOGGER.info("Deployment %s state: %s", uid, state)

                if state == "READY":
                    # Return the configured production URL (not the deployment-specific preview URL)
                    aliases = dep.get("alias", []) or []
                    if aliases:
                        # Use the project's primary production alias, not the preview URL
                        for a in aliases:
                            if "vercel.app" in a and "news-to-me" in a:
                                return f"https://{a}"
                        # Fallback to first alias
                        return f"https://{aliases[0]}"
                    return f"https://web-sand-two-88.vercel.app"

                if state in ("ERROR", "CANCELED", "BUILD_FAILED", "FAILED"):
                    raise RuntimeError(f"Vercel deployment failed: state={state}")

            time.sleep(15)

        raise RuntimeError(
            f"Vercel deployment timed out after {self.timeout}s. "
            "Increase VERCEL_DEPLOY_TIMEOUT or check Vercel dashboard."
        )

    def deploy_and_return_url(self) -> str:
        """Alias for deploy() — kept for backwards compatibility."""
        return self.deploy()


def deploy_via_vercel_cli(branch: str | None = None) -> str:
    """Deploy the web/ directory using Vercel CLI directly.

    Use this when you want to deploy from any branch (e.g., local dev, testing).
    Runs `vercel --prod` which deploys immediately without needing GitHub.

    Args:
        branch: Optional git branch name to include in the deployment name.

    Returns:
        The Vercel deployment URL.
    """
    import subprocess
    web_dir = Path(__file__).resolve().parents[2] / "web"

    cmd = ["vercel", "--yes", "--prod"]
    if branch:
        cmd.extend(["--github", "--github-branch", branch])

    result = subprocess.run(cmd, cwd=web_dir, capture_output=True, text=True)
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
    parser.add_argument("--deploy", action="store_true", help="Deploy via git push to deploy branch (auto)")
    parser.add_argument("--cli", action="store_true", help="Deploy using Vercel CLI directly")
    parser.add_argument("--branch", "-b", default=None, help="Branch name for CLI deploy")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        if args.cli:
            url = deploy_via_vercel_cli(branch=args.branch)
            print(f"Live URL: {url}")
        else:
            url = Deployer().deploy()
            print(f"Live URL: {url}")
    except RuntimeError as e:
        print(f"Deploy failed: {e}", file=__import__("sys").stderr)
        raise SystemExit(1)