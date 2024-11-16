import os
import sys
import re
from subprocess import run


def update_version(new_version):
    with open("version.py", "w") as f:
        f.write(f"VERSION = '{new_version}'")

    with open("config.py", "r") as f:
        content = f.read()

    content = re.sub(
        r'APP_VERSION = "[^"]+"', f'APP_VERSION = "{new_version}"', content
    )

    with open("config.py", "w") as f:
        f.write(content)


def create_release(version):
    version = version.lstrip("v")

    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print("Error: Version must be in format X.Y.Z")
        sys.exit(1)

    update_version(version)

    # Git commands
    commands = [
        ["git", "add", "version.py", "config.py"],
        ["git", "commit", "-m", f"Release version {version}"],
        ["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"],
        ["git", "push"],
        ["git", "push", "origin", f"v{version}"],
    ]

    # Execute git commands
    for cmd in commands:
        result = run(cmd)
        if result.returncode != 0:
            print(f"Error executing command: {' '.join(cmd)}")
            sys.exit(1)

    print(f"\nVersion {version} has been released!")
    print("The GitHub Action will now build and create a release.")
    print("Check the Actions tab on GitHub to monitor progress.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python release.py VERSION")
        print("Example: python release.py 1.0.1")
        sys.exit(1)

    create_release(sys.argv[1])
