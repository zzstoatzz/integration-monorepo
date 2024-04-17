import os
import subprocess
from pathlib import Path


def get_changed_files(previous_tag, current_commit):
    cmd = f"git diff --name-only {previous_tag}..{current_commit}"
    output = subprocess.check_output(cmd, shell=True, text=True)
    return output.strip().split("\n")


def get_changed_integrations(changed_files):
    changed_integrations = set()
    for file_path in changed_files:
        path = Path(file_path)
        if path.parts[0] == "integrations" and path.suffix == ".py":
            changed_integrations.add(path.parts[1])
    return sorted(changed_integrations)


def main():
    previous_tag = os.environ["PREVIOUS_TAG"]
    current_commit = os.environ["CURRENT_COMMIT"]

    changed_files = get_changed_files(previous_tag, current_commit)
    changed_integrations = get_changed_integrations(changed_files)

    if changed_integrations:
        print("Changed integrations:")
        for integration in changed_integrations:
            print(integration)
    else:
        print("No changed integrations found.")


if __name__ == "__main__":
    main()
