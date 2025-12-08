"""Documentation server script for Nodo."""

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Build and serve MkDocs documentation.

    This script serves the documentation locally at http://127.0.0.1:8000.
    It automatically rebuilds when documentation files change.
    """
    # Get the project root (parent of src)
    project_root = Path(__file__).parent.parent.parent.parent

    # Check if mkdocs.yml exists
    mkdocs_yml = project_root / "mkdocs.yml"
    if not mkdocs_yml.exists():
        print("Error: mkdocs.yml not found. Please run this from the project root.")
        sys.exit(1)

    # Change to project root
    os.chdir(project_root)

    # Try to use mkdocs from the current Python environment
    # First try direct command, then try as Python module
    print("Starting MkDocs server...")
    print("Documentation will be available at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server\n")

    try:
        # Try running mkdocs directly first
        subprocess.run(["mkdocs", "serve"], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            # Fallback: run as Python module
            subprocess.run([sys.executable, "-m", "mkdocs", "serve"], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(
                "Error: mkdocs not found. Please install dev dependencies with:"
                "\n  uv sync --dev"
            )
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDocumentation server stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()

