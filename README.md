# Ackredit

[![MolSysSuite: Support Library](https://img.shields.io/badge/MolSysSuite-support%20library-2563eb?labelColor=24292f)](https://github.com/uibcdf/molsyssuite/blob/main/devguide/repository_badges.md#support-library)
[![MolSysSuite policy](https://github.com/uibcdf/ackredit/actions/workflows/molsyssuite-policy.yml/badge.svg?branch=main)](https://github.com/uibcdf/ackredit/actions/workflows/molsyssuite-policy.yml)
[![Python 3.11 | 3.12 | 3.13](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://github.com/uibcdf/molsyssuite/blob/main/devguide/python_policy.md)
[![License](https://img.shields.io/github/license/uibcdf/ackredit)](https://github.com/uibcdf/ackredit/blob/main/LICENSE)

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
