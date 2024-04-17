import os
import subprocess
import sys
from pathlib import Path

import toml

INTEGRATIONS_BASEPATH = "src/integrations"
INTEGRATIONS_VERSIONS_FILE = "src/integrations/versions.toml"


def get_changed_files(previous_tag: str, current_commit: str) -> list[str]:
    cmd = f"git diff --name-only {previous_tag}..{current_commit}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    return output.strip().split("\n")


def get_next_version(integration_name: str, current_version: str) -> str:
    cmd = f"cz bump --dry-run --increment-by 1 --file-name {INTEGRATIONS_VERSIONS_FILE} --key integrations.{integration_name}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    return output.strip().split(" ")[-1]


def get_changed_integrations(
    changed_files: list[str], glob_pattern: str
) -> dict[str, str]:
    integrations_base_path = Path(INTEGRATIONS_BASEPATH)
    changed_integrations = {}
    versions: dict[str, str] = toml.load(Path(INTEGRATIONS_VERSIONS_FILE)).get(
        "integrations", {}
    )

    modified_integrations_files = [
        file_path
        for file_path in changed_files
        if Path(file_path).match(glob_pattern)
        and integrations_base_path in Path(file_path).parents
    ]

    for file_path in modified_integrations_files:
        path = Path(file_path)
        integration_name = path.parent.name
        if integration_name in versions:
            changed_integrations[integration_name] = get_next_version(
                integration_name, versions[integration_name]
            )

    return changed_integrations


def main(glob_pattern: str = "**.py"):
    previous_tag = os.environ.get("PREVIOUS_TAG", "")
    current_commit = os.environ.get("CURRENT_COMMIT", "")

    if not previous_tag or not current_commit:
        print(
            "Error: `PREVIOUS_TAG` or `CURRENT_COMMIT` environment variable is missing."
        )
        return

    changed_files = get_changed_files(previous_tag, current_commit)
    changed_integrations = get_changed_integrations(changed_files, glob_pattern)

    if changed_integrations:
        print(",".join(changed_integrations))
    else:
        print("No changed integrations found.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
