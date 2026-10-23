# Development resource ownership

Reviewed on 2026-10-22 under [Ackredit #132](https://github.com/uibcdf/ackredit/issues/132),
following the [shared policy](../MOLSYSSUITE_GUIDE.md#temporary-development-resources).
This is the component's operation review, not a replacement cleanup framework or
a claim about every execution/platform of third-party tools.

## Maintained operations

| Operation / owner | Resource and useful lifetime | Reviewed disposition and evidence |
| --- | --- | --- |
| `devtools/benchmark.py` | Each persistence sample's journal and scratch directory; needed only during that sample | `ExitStack` closes the writer before `TemporaryDirectory` removes files on either exit. Existing #130 guards cover setup, callback, close and removal failures, and caller protection. Bare/tracked modes create no journal. |
| `devtools/benchmark_lifecycle.py` | Per-study root and per-sample working directories/journals | The study's `TemporaryDirectory` spans worker execution and response parsing. New #132 cases exercise successful calls, failed callbacks and visible cleanup failures; both exceptions survive when operation and cleanup fail. Child processes own cold-import tracing; `Stages` owns only tracing it starts (#131). |
| `devtools/benchmark_provenance.py` | Extracted baseline module; needed until paired rendering finishes | Managed directory covers import and measurement. #132 executes the actual entry point with inert measurements; success/failure removes scratch and retains only an explicitly requested output. No timing/scientific claim follows. |
| `devtools/benchmark_plugins.py` | Fresh process working directories, plus explicitly requested installed-variant destination | Per-sample scratch is managed on both exits. New #132 cases exercise that scope with inert child/build/environment callbacks. Fixture sources, wheels, environments, saved JSON and receipt remain together in the requested destination for verification; the invoking task retires that destination after its last use, including partially completed studies. This does not execute pip or qualify real plugin performance. |
| `devtools/benchmark_portable.py` | In-process sessions, captures and observer scopes; optional receipt path | Session/`ExitStack` scopes restore state on exit. No scratch/environment allocation; the caller owns the requested receipt. Existing provider/session tests cover the runtime scopes. Source inspection, not a new benchmark run. |
| `devtools/benchmark_public_installation.py` | Caller-supplied public/control environments and receipts; temporary samples delegated to lifecycle study | Inventories and verifies both prefixes without removing them. Reuses the lifecycle scratch owner; the installation task owns environment retirement. Existing footprint/provenance guards remain separate from a fresh solver/public installation. |
| `devtools/check_publication_tools.py`, `check_biblatex.py`, `check_jabref.py` | Explicit new output directory: original attribution, exports, process streams, reader/style/PDF results and isolated engine preferences/caches | Prior destinations are refused. Outputs survive failure for diagnosis; subprocess exit status and exact byte streams are retained. Existing receiving guards exercise failure, refusal and input protection. The task removes the destination once no longer useful; probes never remove supplied tool distributions or inputs. No new real-engine/version qualification is claimed here. |
| `devtools/qualification_bundle.py` | Explicit new bundle directory, immutable candidate/producer/released files and manifest; aggregate receipt | Requested outputs persist for receiving and digest verification, including partial failed builds. Sources and supplied candidate files are inputs, not disposable scratch. The release task retires local copies after required verification; existing receipt/artifact retention and immutable published coordinates remain separate. Source review and existing bundle guards; no build/upload in this review. |
| `devtools/qualification/test_pyunitwizard.py` | Explicit `ACKREDIT_QUALIFICATION_OUTPUT`, saved results, events and receiving proofs | Caller/job owns the directory. Failure evidence is intentionally retained; fresh-reader subprocesses terminate normally or expose errors. Ordinary resource checks do not rerun its real scientific release gate. |
| `devtools/refresh_example_notebook.py` | Jupyter kernel/connection resources and explicitly updated notebook | `NotebookClient.execute()` owns kernel lifetime; output writes occur after successful execution. Notebook is maintained source/output, not scratch to delete. Source inspection only; this review does not reexecute the notebook or certify Jupyter internals. |
| `devtools/check_dependency_routes.py`, `installed_smoke.py`, `ci_backlog.py` | Supplied checkouts/prefixes, synchronous subprocesses, HTTP response and runner-owned `GITHUB_OUTPUT` | Read-only checks except the explicit runner output append. File/HTTP contexts and synchronous subprocess owners remain visible; errors propagate. No custom disposable filesystem root. Shared preflight implementation remains MolSysSuite-owned. |
| `devtools/devguide_index.py`, `devguide_reports.py` | Maintained report indexes and read-only report inputs | Explicit repository outputs, not temporary evidence. No disposable environment; file operations are scoped. |
| `tests/` | Pytest `tmp_path`/`tmp_path_factory`, isolated subprocess outputs, managed CSL fixture/compiled `.pyc`, session-file contract fixture | Test invocation owns its base directory and retained failure evidence. Existing managed fixtures clean on exit; #130 covers the session-contract failures. Pytest-managed retention is not permission to sweep other invocations. This task runs selected tests in its own managed base directory and removes it after extracting the result. |
| `docs/` | Explicit Sphinx output/doctrees/cache | Invoking build owns the output; keep only while rendering/checking it. `_build` and notebook checkpoints are excluded from source collection. This task uses a managed build destination; existing repeatability checks remain applicable. |
| `.github/workflows/CI*.yaml`, `python314_feasibility.yaml`, `coverage.yaml` | Hosted job environments, installed files, `RUNNER_TEMP`, test roots, docs/coverage outputs | Hosted job-scoped resources; artifacts have their own declared retention. Source inspection of current callers, not an observed destruction receipt or a self-hosted-runner cleanup guarantee. No self-hosted route is declared. |
| `.github/workflows/function_provider_receiving.yaml` | Hosted bundle, per-cell installed environments and receiving outputs | Explicit bundle/matrix/cell artifacts retain 30-day workflow retention; cell evidence uploads use `always()`. These existing artifact contracts do not require local workspaces to survive after receiving/closeout. Source inspection only. |
| Conda build, installed and promotion wrappers | Pinned shared-provider checkout, build roots, exact archive and verification outputs | MolSysSuite/shared action owns implementation; Ackredit's release task owns any local qualification prefixes/caches it creates. Local recipe/build script creates package payload in the supplied build prefix. Review an actual local release's exact paths before disposing them; never remove the active shared Conda environment or original public artifact. No release executed by this review. |

No missing Ackredit-owned scratch cleanup was reproduced in the remaining
reviewed operations. No implementation exception is needed for this reviewed
scope. Deliberately retained output is ordinary ownership, not an exception.
Dependency-manager caches, Jupyter internals, hosted runner retirement and shared
provider internals are not newly executed or universally certified here.

## Retained resources and closeout

The original 55 explicit historical paths recorded in the central 2026-10-10
inventory were rechecked individually: 54 are absent and `/tmp/pytest-of-diego`
exists as a shared invocation root. Absence does not identify who removed paths
or establish a complete inventory. Twelve registered `/tmp` worktree paths
were also absent. Every recorded worktree commit is reachable from `origin/main`.
After a dry run, `git worktree prune --expire now --verbose` removed only their
stale registrations. No worktree files, branches or shared environments were
deleted. Historical receipt/source identities remain unchanged.

At the initial 2026-10-22 inspection, there were no direct Ackredit-prefixed
entries in `/tmp`. `/tmp/pytest-of-diego` is shared across invocations and is not
owned or deleted by this review. Prefix matching was an inventory aid, never a
deletion rule. Filesystem usage was 2.9 GiB of the 16 GiB tmpfs; capacity is a
dated observation, not evidence of who cleaned earlier resources.

The invoking task owns its `ackredit132-*` managed test/documentation directories.
They are removed after extracting applicable results, including failure paths;
normalized source/validation observations live in the owning report and receipt.
There is no obligation to relocate needed evidence outside `/tmp` or impose an
arbitrary retention period. Future tasks may retain necessary evidence there
and must retire it when its usefulness ends, following the shared policy.

The durable guard `tests/test_tool_resource_lifecycle.py` checks the remaining
three scratch owners. Existing #130/#131 and receiving guards cover their
separate boundaries. Tests with inert callbacks establish lifecycle, not
scientific equivalence, installed dependency closure or benchmark performance.
