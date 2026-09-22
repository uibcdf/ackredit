"""The example workflow, as a script and as a notebook, is held to what it does.

The example libraries show Ackredit inside a host. These show it from the other
side: a user who runs an analysis and asks for the references at the end, which
is the one thing a user of a host library actually does.

The notebook is stored with its outputs, so it reads on GitHub without running,
and the documentation does not execute notebooks. Stored output is a quotation,
and a quotation drifts; this executes every cell without a kernel and requires
the stored output to be what the code produces now. When it fails, run
`python devtools/refresh_example_notebook.py`.
"""

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
NOTEBOOK = EXAMPLES / "workflow.ipynb"

TITLES = [
    "A workflow for dummy analyses",
    "A direct method for dummy systems",
    "An iterative refinement for dummy systems",
    "Reference dummy measurements",
]

REFRESH = "run `python devtools/refresh_example_notebook.py`"


# --- the script -------------------------------------------------------------


@pytest.fixture(scope="module")
def script_run(tmp_path_factory):
    output = tmp_path_factory.mktemp("citations")
    result = subprocess.run(
        [sys.executable, str(EXAMPLES / "workflow.py"), str(output)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    return result, output


def test_the_script_runs(script_run):
    result, _ = script_run
    assert result.returncode == 0, result.stderr[-1500:]


def test_the_script_reports_every_citation_the_run_reached(script_run):
    result, _ = script_run
    for title in TITLES:
        assert title in result.stdout


def test_the_script_leaves_the_files_for_a_manuscript(script_run):
    _, output = script_run
    written = sorted(path.name for path in output.iterdir())

    assert written == [
        "ackredit_report.bib",
        "ackredit_report.md",
        "ackredit_report.tex",
        "ackredit_report.txt",
    ]
    bibliography = (output / "ackredit_report.bib").read_text(encoding="utf-8")
    assert bibliography.count("@") == len(TITLES)


# --- the notebook -----------------------------------------------------------


def _stored(cell: dict) -> dict:
    """What the notebook says the cell printed and displayed."""
    stored = {"stdout": "", "html": None, "plain": None}
    for output in cell["outputs"]:
        if output["output_type"] == "stream" and output["name"] == "stdout":
            stored["stdout"] += "".join(output["text"])
        elif output["output_type"] == "execute_result":
            data = output["data"]
            if "text/html" in data:
                stored["html"] = "".join(data["text/html"])
            stored["plain"] = "".join(data.get("text/plain", ""))
    return stored


# One fresh interpreter for the whole notebook, as one kernel would be, run from
# the directory a user opens it in.
_RUNNER = textwrap.dedent(
    """
    import ast, contextlib, io, json, sys

    sys.path.insert(0, ".")
    notebook = json.load(open(sys.argv[1], encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    results = []

    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        tree = ast.parse("".join(cell["source"]))
        last = tree.body[-1] if tree.body and isinstance(tree.body[-1], ast.Expr) else None
        body = ast.Module(body=tree.body[:-1] if last else tree.body, type_ignores=[])
        captured, value = io.StringIO(), None
        with contextlib.redirect_stdout(captured):
            exec(compile(body, "<cell>", "exec"), namespace)
            if last is not None:
                value = eval(compile(ast.Expression(last.value), "<cell>", "eval"), namespace)
        results.append({
            "stdout": captured.getvalue(),
            "html": value._repr_html_() if hasattr(value, "_repr_html_") else None,
            "plain": None if value is None else repr(value),
        })

    print(json.dumps(results))
    """
)


@pytest.fixture(scope="module")
def notebook():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def produced(notebook):
    result = subprocess.run(
        [sys.executable, "-c", _RUNNER, str(NOTEBOOK)],
        capture_output=True,
        text=True,
        cwd=str(EXAMPLES),
    )
    assert result.returncode == 0, result.stderr[-1500:]
    return json.loads(result.stdout)


def _code_cells(notebook):
    return [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]


def test_the_notebook_was_run_top_to_bottom(notebook):
    """Stored output from cells run out of order describes no run anyone can repeat."""
    counts = [cell["execution_count"] for cell in _code_cells(notebook)]
    assert counts == list(range(1, len(counts) + 1)), f"{counts}; {REFRESH}"


def test_the_notebook_stores_no_error(notebook):
    for cell in _code_cells(notebook):
        kinds = [output["output_type"] for output in cell["outputs"]]
        assert "error" not in kinds, "".join(cell["source"])


def test_every_stored_output_is_what_the_cell_produces_now(notebook, produced):
    cells = _code_cells(notebook)
    assert len(cells) == len(produced)

    for cell, now in zip(cells, produced):
        stored = _stored(cell)
        source = "".join(cell["source"])
        for kind in ("stdout", "html", "plain"):
            assert stored[kind] == now[kind], (
                f"the stored {kind} of `{source.splitlines()[0]}` is not what it "
                f"produces now; {REFRESH}"
            )


def test_the_notebook_shows_every_citation_the_run_reached(notebook):
    shown = json.dumps(notebook)
    for title in TITLES:
        assert title in shown


def test_running_a_cell_again_cites_nothing_twice():
    """The notebook tells its reader this, so it is checked rather than hoped."""
    script = textwrap.dedent(
        """
        import ackredit, dummy_pipeline
        dummy_pipeline.analyse("s", method="iterative", use_reference=True)
        once = {k: list(v) for k, v in ackredit.get_used_items().items()}
        dummy_pipeline.analyse("s", method="iterative", use_reference=True)
        twice = {k: list(v) for k, v in ackredit.get_used_items().items()}
        assert once == twice, (once, twice)
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=str(EXAMPLES),
    )
    assert result.returncode == 0, result.stderr[-1500:]
