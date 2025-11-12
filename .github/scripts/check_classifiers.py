import ast
import re
import sys
from pathlib import Path

import requests


def get_classifier_tags():
    """Get PyPI classifier tags by parsing the HTML page.

    Fetches the PyPI classifiers page and extracts all valid classifier
    tags using regex pattern matching.

    Returns:
        list[str]: A list of valid PyPI classifier strings.

    Raises:
        requests.RequestException: If the HTTP request to PyPI fails.
    """
    response = requests.get("https://pypi.org/classifiers/")
    response.raise_for_status()

    # Extract classifier names from the HTML using regex
    # Look for data-clipboard-target="source">CLASSIFIER_NAME</a>
    pattern = r"data-clipboard-target=\"source\">([^<]+)</a>"
    classifiers = re.findall(pattern, response.text)

    return classifiers


def extract_classifiers_from_setup():
    """Extract classifier tags from setup.py file.

    Parses the setup.py file using AST to find the setup() function call
    and extracts the classifiers argument value. Handles both direct
    setup() calls and setuptools.setup() calls.

    Returns:
        list[str]: A list of classifier strings found in setup.py, or
            an empty list if setup.py doesn't exist or no classifiers
            are found.
    """
    path = Path("setup.py")
    if not path.exists():
        print("⚠️ setup.py not found — skipping classifier check")
        return []
    source = path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Handle both 'setup()' and 'setuptools.setup()'
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name == "setup":
                for kw in node.keywords:
                    if kw.arg == "classifiers" and isinstance(
                        kw.value, (ast.List, ast.Tuple)
                    ):
                        classifiers = []
                        for elt in kw.value.elts:
                            # Handle both ast.Constant (Python 3.8+) and ast.Str (older versions)
                            if isinstance(elt, ast.Constant):
                                classifiers.append(elt.value)
                            elif isinstance(elt, ast.Str):  # Python < 3.8
                                classifiers.append(elt.s)
                        return classifiers
    return []


def main():
    """Main entry point for classifier validation.

    Validates that all classifiers in setup.py are valid PyPI classifiers.
    Fetches the list of valid classifiers from PyPI and compares them
    against the classifiers found in setup.py.

    Exits with code 1 if any invalid classifiers are found, otherwise
    prints a success message.
    """
    valid = get_classifier_tags()
    classifiers = extract_classifiers_from_setup()
    if not classifiers:
        print("⚠️ No classifiers found in setup.py")
        return None
    invalid = [c for c in classifiers if c not in valid]
    if invalid:
        print("❌ Invalid classifiers found:")
        for c in invalid:
            print(f"  - {c}")
        sys.exit(1)
    else:
        print("✅ All classifiers are valid!")
    return None


if __name__ == "__main__":
    main()
