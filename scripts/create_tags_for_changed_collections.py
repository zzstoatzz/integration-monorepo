import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from gh_util.functions import create_repo_tag, fetch_latest_repo_tag
from packaging.version import Version

INTEGRATIONS_BASEPATH = "src/integrations"
OWNER = "zzstoatzz"
REPO = "integration-monorepo"


def get_changed_files(previous_tag: str, current_commit: str) -> List[str]:
    cmd = f"git diff --name-only {previous_tag}..{current_commit}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    return output.strip().split("\n")


def increment_patch_version(version: str) -> str:
    v = Version(version)
    return f"{v.major}.{v.minor}.{v.micro + 1}"


async def get_changed_integrations(
    changed_files: List[str], glob_pattern: str
) -> Dict[str, str]:
    integrations_base_path = Path(INTEGRATIONS_BASEPATH)
    changed_integrations = {}
    modified_integrations_files = [
        file_path
        for file_path in changed_files
        if Path(file_path).match(glob_pattern)
        and integrations_base_path in Path(file_path).parents
    ]
    for file_path in modified_integrations_files:
        path = Path(file_path)
        integration_name = path.parent.name
        ref = await fetch_latest_repo_tag(OWNER, REPO, f"{integration_name}-*")
        changed_integrations[integration_name] = increment_patch_version(
            ref.object.tag.replace("refs/tags/", "")
        )
    return changed_integrations


async def create_tags(changed_integrations: Dict[str, str]) -> None:
    for integration_name, version in changed_integrations.items():
        await create_repo_tag(
            owner=OWNER,
            repo=REPO,
            tag_name=f"{integration_name}-{version}",
            commit_sha=os.environ.get("CURRENT_COMMIT", ""),
            message=f"Release {integration_name} {version}",
        )


async def main(glob_pattern: str = "**/*.py"):
    previous_tag = os.environ.get("PREVIOUS_TAG", "")
    current_commit = os.environ.get("CURRENT_COMMIT", "")

    if not previous_tag or not current_commit:
        raise ValueError(
            "Error: `PREVIOUS_TAG` or `CURRENT_COMMIT` environment variable is missing."
        )

    changed_files = get_changed_files(previous_tag, current_commit)

    if changed_integrations := await get_changed_integrations(
        changed_files, glob_pattern
    ):
        await create_tags(changed_integrations)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(main(sys.argv[1]))
    else:
        asyncio.run(main())
