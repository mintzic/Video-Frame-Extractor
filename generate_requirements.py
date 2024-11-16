import subprocess
import sys
import os
from pip._internal.operations.freeze import freeze


def get_project_imports():
    """Get all imported packages from project files"""
    imports = set()
    project_files = []

    # Get all .py files in the current directory and subdirectories
    for root, dirs, files in os.walk("."):
        if ".venv" in dirs:  # Skip virtual environment directory
            dirs.remove(".venv")
        if "venv" in dirs:  # Skip virtual environment directory
            dirs.remove("venv")
        for file in files:
            if file.endswith(".py"):
                project_files.append(os.path.join(root, file))

    # Standard library modules to ignore
    stdlib_modules = {
        "os",
        "sys",
        "datetime",
        "time",
        "json",
        "typing",
        "threading",
        "queue",
        "logging",
    }

    # Read each file and extract import statements
    for file_path in project_files:
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                content = file.read()
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line.startswith("import ") or line.startswith("from "):
                        # Extract package name
                        if line.startswith("import "):
                            package = line.split()[1].split(".")[0]
                        else:
                            package = line.split()[1].split(".")[0]
                        if package not in stdlib_modules:
                            imports.add(package)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return imports


def generate_requirements():
    """Generate requirements.txt with only used packages"""
    print("Analyzing project files...")
    project_imports = get_project_imports()

    print("\nFound the following package imports:")
    for imp in sorted(project_imports):
        print(f"- {imp}")

    print("\nGetting package versions...")
    requirements = []

    # Get all installed packages
    for req in freeze():
        package_name = req.split("==")[0].lower()
        if package_name in [imp.lower() for imp in project_imports]:
            requirements.append(req)

    # Add essential packages if not already included
    essential_packages = {"moviepy", "numpy", "Pillow", "pyinstaller"}

    # Add essential packages that aren't already in requirements
    current_packages = {req.split("==")[0].lower() for req in requirements}
    for package in essential_packages:
        if package.lower() not in current_packages:
            try:
                print(f"Installing missing essential package: {package}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                # Get the version of the newly installed package
                for req in freeze():
                    if req.split("==")[0].lower() == package.lower():
                        requirements.append(req)
                        break
            except Exception as e:
                print(f"Error installing {package}: {e}")

    print("\nGenerating requirements.txt...")
    with open("requirements.txt", "w") as f:
        for req in sorted(requirements):
            f.write(f"{req}\n")

    print("\nDone! Requirements file generated.")
    print("Contents of requirements.txt:")
    with open("requirements.txt", "r") as f:
        print(f.read())


if __name__ == "__main__":
    generate_requirements()
