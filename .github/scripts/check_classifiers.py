import ast
import requests
import sys
from pathlib import Path
import re


def get_classifier_tags():
    """Get PyPI classifier tags by parsing the HTML page."""
    response = requests.get("https://pypi.org/classifiers/")
    response.raise_for_status()
    
    # Extract classifier names from the HTML using regex
    # Look for data-clipboard-target="source">CLASSIFIER_NAME</a>
    pattern = r'data-clipboard-target="source">([^<]+)</a>'
    classifiers = re.findall(pattern, response.text)
    
    return classifiers


def extract_classifiers_from_setup():
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
                    if kw.arg == "classifiers" and isinstance(kw.value, (ast.List, ast.Tuple)):
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
