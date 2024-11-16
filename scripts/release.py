import os
import sys
import re
from subprocess import run


def update_version(new_version):
    # Update version.py in scripts directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Update version files in both locations
    version_files = [
        os.path.join(script_dir, "version.py"),
        os.path.join(project_root, "src", "version.py"),
    ]

    for version_file in version_files:
        with open(version_file, "w") as f:
            f.write(f"VERSION = '{new_version}'")

    # Update config.py in src directory
    config_path = os.path.join(project_root, "src", "config.py")
    with open(config_path, "r") as f:
        content = f.read()

    content = re.sub(
        r'APP_VERSION = "[^"]+"', f'APP_VERSION = "{new_version}"', content
    )

    with open(config_path, "w") as f:
        f.write(content)


def create_release(version):
    # Remove 'v' prefix if present
    version = version.lstrip("v")

    # Validate version format
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print("Error: Version must be in format X.Y.Z")
        sys.exit(1)

    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Change to project root directory
    os.chdir(project_root)

    # Update version files
    update_version(version)

    # Git commands
    commands = [
        ["git", "add", "src/version.py", "src/config.py", "scripts/version.py"],
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
