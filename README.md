# Ackredit

Acknowledge what you used, credit what matters.

**Ackredit** is a runtime citation and acknowledgement tracking engine for scientific
workflows in Python. Instead of asking users to cite a whole library because they
installed it, Ackredit records which algorithms, datasets and dependencies a run
actually reached, and turns that into a citation report with full provenance.

It is a MolSysSuite component, designed as an optional dependency: a host library keeps
working when Ackredit is absent.

Read [`MOLSYSSUITE_GUIDE.md`](MOLSYSSUITE_GUIDE.md) and [`AGENTS.md`](AGENTS.md) before
contributing, and [`standards/ACKREDIT_GUIDE.md`](standards/ACKREDIT_GUIDE.md) to
integrate Ackredit into a host library.
