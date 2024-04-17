import os
import subprocess
import sys
from pathlib import Path

INTEGRATIONS_PATH = "src/integrations"


def get_changed_files(previous_tag: str, current_commit: str) -> list[str]:
    cmd = f"git diff --name-only {previous_tag}..{current_commit}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    return output.strip().split("\n")


def get_changed_integrations(changed_files: list[str], glob_pattern: str) -> list[str]:
    integrations_base_path = Path(INTEGRATIONS_PATH)
    changed_integrations = set()

    for file_path in changed_files:
        path = Path(file_path)
        if path.match(glob_pattern) and integrations_base_path in path.parents:
            changed_integrations.add(path.parent.name)

    return sorted(changed_integrations)


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
