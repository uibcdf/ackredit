"""A user's workflow over two host libraries, collecting its citations at the end.

Run it from the repository root:

    python examples/workflow.py [output-directory]

Nothing in the analysis mentions Ackredit. The libraries record what the run
used as it happens, and the workflow only asks at the end. The citation files
are written to `citations/` unless another directory is given.
"""

import sys
from pathlib import Path

import dummy_pipeline

import ackredit

# The analysis. Two samples, treated differently: only the second is refined,
# and only the second is compared against the reference dataset.
print(dummy_pipeline.analyse("sample 1"))
print(dummy_pipeline.analyse("sample 2", method="iterative", use_reference=True))

# What the run used.
print()
print(ackredit.report())

# Why each one was cited.
print()
print(ackredit.report(format="provenance"))

# The files for the manuscript.
output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("citations")
ackredit.dump(output)
print()
print(f"written to {output}/: " + ", ".join(sorted(p.name for p in output.iterdir())))
