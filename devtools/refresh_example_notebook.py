"""Re-execute `examples/workflow.ipynb` so its stored outputs are current.

The notebook is kept with its outputs so it reads on GitHub without running,
and `tests/test_example_workflow.py` fails when they no longer match what the
code produces. This is how to bring them back:

    python devtools/refresh_example_notebook.py

It needs Jupyter, which the development environment provides. The kernel runs
in `examples/`, the directory a user opens the notebook from.
"""

from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "examples" / "workflow.ipynb"


def main() -> None:
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOK.parent)}},
    ).execute()
    # The interpreter's patch level is not part of the example, and recording it
    # would rewrite the file on every machine that refreshes it.
    notebook.metadata.pop("language_info", None)
    nbformat.write(notebook, NOTEBOOK)
    print(f"refreshed {NOTEBOOK.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
