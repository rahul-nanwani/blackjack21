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
        list[str]: A list of valid classifier strings.

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


def _load_pyproject() -> dict:
    path = Path("pyproject.toml")
    if not path.exists():
        return {}
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    with path.open("rb") as f:
        return tomllib.load(f)


def extract_classifiers_from_pyproject():
    """Extract classifier tags from [project] in pyproject.toml."""
    data = _load_pyproject()
    return data.get("project", {}).get("classifiers") or []


def extract_classifiers_from_setup():
    """Extract classifier tags from setup.py (legacy layout)."""
    path = Path("setup.py")
    if not path.exists():
        return []
    source = path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name == "setup":
                for kw in node.keywords:
                    if kw.arg == "classifiers" and isinstance(
                        kw.value,
                        (ast.List, ast.Tuple),
                    ):
                        classifiers = []
                        for elt in kw.value.elts:
                            if isinstance(elt, ast.Constant):
                                classifiers.append(elt.value)
                            elif isinstance(elt, ast.Str):  # Python < 3.8
                                classifiers.append(elt.s)
                        return classifiers
    return []


def extract_classifiers():
    """Prefer pyproject.toml [project.classifiers], else setup.py."""
    from_pp = extract_classifiers_from_pyproject()
    if from_pp:
        return from_pp
    return extract_classifiers_from_setup()


def main():
    """Validate classifiers against the live PyPI classifier list."""
    valid = get_classifier_tags()
    classifiers = extract_classifiers()
    if not classifiers:
        print("⚠️ No classifiers found in pyproject.toml or setup.py")
        return
    invalid = [c for c in classifiers if c not in valid]
    if invalid:
        print("❌ Invalid classifiers found:")
        for c in invalid:
            print(f"  - {c}")
        sys.exit(1)
    else:
        print("✅ All classifiers are valid!")
    return


if __name__ == "__main__":
    main()
