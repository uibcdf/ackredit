# Ackredit

[![MolSysSuite: Support Library](https://img.shields.io/badge/MolSysSuite-support%20library-2563eb?labelColor=24292f)](https://github.com/uibcdf/molsyssuite/blob/main/devguide/repository_badges.md#support-library)
[![MolSysSuite policy](https://github.com/uibcdf/ackredit/actions/workflows/molsyssuite-policy.yml/badge.svg?branch=main)](https://github.com/uibcdf/ackredit/actions/workflows/molsyssuite-policy.yml)
[![Python 3.11 | 3.12 | 3.13](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://github.com/uibcdf/molsyssuite/blob/main/devguide/python_policy.md)
[![License](https://img.shields.io/github/license/uibcdf/ackredit)](https://github.com/uibcdf/ackredit/blob/main/LICENSE)

[![Tests](https://github.com/uibcdf/ackredit/actions/workflows/CI.yaml/badge.svg?branch=main)](https://github.com/uibcdf/ackredit/actions/workflows/CI.yaml)
[![Codecov](https://codecov.io/gh/uibcdf/ackredit/branch/main/graph/badge.svg)](https://app.codecov.io/gh/uibcdf/ackredit)

Coverage shows the last uploaded Linux/Python 3.14 runtime line report from the
selected full test suite. It runs weekly and on manual dispatch and may lag later
internal commits. Generated version constants, dependencies, subprocesses and
developer tools are outside that percentage; optional system-tool tests may skip
when their engines are absent. It does not certify scientific correctness or the
full platform/interpreter matrix. See the [coverage scope and evidence](devguide/archive/scoped_runtime_coverage.md).

Acknowledge what you used, credit what matters.

**Ackredit** is a runtime citation and acknowledgement tracking engine for scientific
workflows in Python. Instead of asking users to cite a whole library because they
installed it, Ackredit records which algorithms, datasets and dependencies a run
actually reached, and turns that into a citation report with full provenance.

It is a MolSysSuite component, designed as an optional dependency: a host library keeps
working when Ackredit is absent.

The required source contract is Python 3.11–3.14. Qualification and public
installed delivery are tracked in [Ackredit #80](https://github.com/uibcdf/ackredit/issues/80);
the badge retains the previously verified range until admission.

Read [`MOLSYSSUITE_GUIDE.md`](MOLSYSSUITE_GUIDE.md) and [`AGENTS.md`](AGENTS.md) before
contributing, and [`standards/ACKREDIT_GUIDE.md`](standards/ACKREDIT_GUIDE.md) to
integrate Ackredit into a host library.
