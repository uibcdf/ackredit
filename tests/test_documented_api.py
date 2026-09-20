"""Every Python snippet in the documentation must reference an API that exists.

Documentation is not executed by the test suite, so a snippet can keep teaching an
import that raises ImportError for as long as nobody types it out. This checks the
whole class of defect at once: it parses every documented snippet and resolves each
name it imports from, or reads off, the ``ackredit`` package.

It does not execute snippets. They reference host libraries that are not installed
here, which is fine: the failures worth catching are name resolution, not runtime.
"""

import ast
import importlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Every guide synchronized from another repository carries this marker. Their
# content is owned and reviewed there, and their snippets describe that library's
# API rather than ours, so they are not held to Ackredit's.
VENDORED_MARKER = "SYNCHRONIZED MOLSYSSUITE GUIDE — DO NOT EDIT COMPONENT COPIES."

# Archived reports quote the defective code they describe. That evidence must stay
# exactly as it was written, so it is not held to the current API.
EXCLUDED_DIRS = (Path("devguide") / "archive",)

PACKAGE = "ackredit"


def _markdown_blocks(path: Path):
    """Yield (first_line_number, source) for each ```python block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    inside, start, buffer = False, 0, []
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not inside and stripped in ("```python", "```py"):
            inside, start, buffer = True, number + 1, []
        elif inside and stripped == "```":
            yield start, "\n".join(buffer)
            inside = False
        elif inside:
            buffer.append(line)


def _notebook_blocks(path: Path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook.get("cells", []), 1):
        if cell.get("cell_type") == "code":
            yield index, "".join(cell.get("source", []))


def _documented_snippets():
    """All (label, source) pairs found in repository documentation."""
    found = []
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if ".git" in path.parts:
            continue
        if any(relative.is_relative_to(directory) for directory in EXCLUDED_DIRS):
            continue
        if VENDORED_MARKER in path.read_text(encoding="utf-8"):
            continue
        for line, source in _markdown_blocks(path):
            found.append((f"{path.relative_to(ROOT)}:{line}", source))
    for path in sorted(ROOT.rglob("*.ipynb")):
        if ".git" in path.parts or ".ipynb_checkpoints" in path.parts:
            continue
        for cell, source in _notebook_blocks(path):
            found.append((f"{path.relative_to(ROOT)} cell {cell}", source))
    return found


SNIPPETS = _documented_snippets()


def _resolves(module_name: str, attribute: str) -> bool:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return False
    if hasattr(module, attribute):
        return True
    try:
        importlib.import_module(f"{module_name}.{attribute}")
    except ImportError:
        return False
    return True


def _referenced_names(tree: ast.AST):
    """Yield (module, attribute) pairs the snippet expects ackredit to provide."""
    aliased_as_module = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Relative imports belong to the host's own package, not to ours.
            if node.level or not node.module:
                continue
            if node.module == PACKAGE or node.module.startswith(f"{PACKAGE}."):
                for alias in node.names:
                    if alias.name != "*":
                        yield node.module, alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == PACKAGE or alias.name.startswith(f"{PACKAGE}."):
                    aliased_as_module.add(alias.asname or alias.name.split(".")[0])

    if not aliased_as_module:
        return

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in aliased_as_module
        ):
            yield PACKAGE, node.attr


def test_documentation_contains_python_snippets():
    """Guard the guard: a broken extractor would make everything below vacuous."""
    assert len(SNIPPETS) > 20


@pytest.mark.parametrize("label,source", SNIPPETS, ids=[s[0] for s in SNIPPETS])
def test_snippet_parses(label, source):
    try:
        ast.parse(source)
    except SyntaxError as error:
        pytest.fail(f"{label}: documented snippet is not valid Python: {error}")


@pytest.mark.parametrize("label,source", SNIPPETS, ids=[s[0] for s in SNIPPETS])
def test_snippet_references_an_api_that_exists(label, source):
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("covered by test_snippet_parses")

    missing = [
        f"{module}.{attribute}"
        for module, attribute in _referenced_names(tree)
        if not _resolves(module, attribute)
    ]

    assert not missing, (
        f"{label}: documented but missing: {', '.join(sorted(set(missing)))}"
    )
