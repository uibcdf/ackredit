(About_Performance)=
# What Ackredit costs

Numbers below retain their own dates, sources and measurement boundaries.
`devtools/benchmark.py` covers the historical MolSysMT workflow;
`devtools/benchmark_portable.py` covers warmed repeated credits;
`devtools/benchmark_lifecycle.py` adds fresh-process stages and separate
Python-allocation measurements. Each is runnable in the stated environment.

(published-diagnostic-providers-2026-10-06)=
## Published diagnostic providers (2026-10-06)

[#119](https://github.com/uibcdf/ackredit/issues/119) repeats the public receiving
measurement after SMonitor **0.19.0** and ArgDigest **0.15.0** are published.
Earlier #115 source-wheel evidence and #118's public 0.18.0/0.14.0 inventory
retain their original identities below. This new Linux x86-64/Python 3.14.8
environment selects exact ordinary-channel `smonitor=0.19.0=py_1` and
`argdigest=0.15.0=py_0`, with the unchanged public Ackredit 0.11.0 archive.

The [new raw receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/public_providers_119_2026-10-06.json)
retains independently verified registry/index coordinates and actual installed
provider origins. Public SMonitor's archive SHA-256 is
`4b876b4993b1e2caeed40851402a931f3b245ed7c1916d9483d81bc90274e31c`;
ArgDigest's is
`b0f22038a8ad1c888dca10adedaca0fa14d2383a685a97c0602b7ca05f29d6a1`.
Only those two package coordinates differ from #118. The same 24 Python-control
packages remain unchanged, and the six-package increment is now **538,236
compressed bytes (526 KiB)** and **2,718,363 recorded regular-file bytes
(2.59 MiB)**. There is still no NumPy in the core receiving environment.
The metric definitions and limits of the earlier section apply unchanged.

Twenty fresh-process samples use seven timing and three separate allocation
rounds for each of the two original cases. Cold import has median **177.11 ms**,
range 154.13–184.80 ms, and median traced peak **10.67 MiB**. The one-reference
first workflow report has median 1.211 ms. These are unpaired measurements
against a different provider set; they do not establish a causal speedup over
#118 or the developer-wheel studies.

The isolated receiving guards configure the application before importing
Ackredit, then check preserved policy, available catalog codes, repeated
registration and pure audience-specific rendering. Explicit restrictive
scopes preserve active Ackredit argument refusals, provider binding/pipelines,
the native exception object and cause, and every independent result's original
bibliography. Instrumented argument/native-error conversions remain zero for
the controlled fixture, including a failed normalization pipeline. This is a
test of automatic provider-owned capture, not general redaction of original
citations, caller-supplied context or explicitly formatted metadata.

Both the original public Ackredit file and a normally installed current-runtime
wheel execute these guards with the new public providers. The fixture's explicit
`argument_digestion=False` tests ArgDigest pipeline semantics; Ackredit's own
compatible digestion defaults and four dependency floors remain unchanged.
Runtime source `9a27f1b4f46c9392f911670f90ad7e8b12ff56c8` is built separately as
`0.11.0+20.g9a27f1b`; it is a development candidate, not another public release.

For a designated lane, run from outside the checkout:

```bash
python -m pytest --receptor=llm --require-scoped-providers /path/to/ackredit/tests/test_published_diagnostic_providers.py
```

`--require-scoped-providers` rejects unavailable capabilities rather than
skipping. Ordinary lower-bound environments may skip only these optional new
capability checks. To probe a separate untouched public interpreter without
adding pytest to its core closure, the runner also accepts
`--diagnostic-receiving-python /path/to/public/bin/python`; the isolated children
remove `PYTHONPATH` and execute there.

Reproduce the footprint with the previous commands, adding exact provider pins
to `conda create` and verifying all three public files with the shared verifier's
`--inventory` JSON route. Run `benchmark_public_installation.py` with
`--issue uibcdf/ackredit#119`; its original default remains #118. Wider platform,
scientific-workload and host-release qualification remain separate. Consumer
coordination stays in [MolSysSuite #106](https://github.com/uibcdf/molsyssuite/issues/106).

(public-conda-installation-2026-10-06)=
## Public Conda installation (2026-10-06)

[#118](https://github.com/uibcdf/ackredit/issues/118) measures the documented
public route on Linux x86-64/Python 3.14.8. Native Conda creates two new
environments with separate initially empty package/repodata caches, strict
`uibcdf`, `conda-forge` priority and no default package additions: Python alone,
and Python plus `ackredit=0.11.0=py_0`. All 24 control packages retain exactly
the same versions, builds and archive hashes in the 30-package receiving
environment. The Python control includes pip and the interpreter's native
dependencies; it is not just the Python executable's size.

The [raw receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/public_installation_118_2026-10-06.json)
retains every package's public URL, hash, dependency list and measured file
counts, plus installed smoke behavior, the shared public-registry verification,
tool hashes and 20 raw lifecycle samples. The original Ackredit archive remains
115,481 bytes, SHA-256
`df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f`,
from producer `85deae594e65b2fd443d6ca9a7347eb2bda537e1`. Nothing is rebuilt or
published by this study.

| Added package | Version/build | Compressed archive, KiB | Recorded regular files, MiB |
| --- | --- | ---: | ---: |
| Ackredit | 0.11.0 / py_0 | 112.77 | 0.647 |
| ArgDigest | 0.14.0 / py_0 | 50.41 | 0.338 |
| DepDigest | 0.13.0 / py_0 | 25.75 | 0.094 |
| SMonitor | 0.18.0 / py_0 | 49.49 | 0.386 |
| PyYAML | 6.0.3 / py314h67df5f8_1 | 197.65 | 0.702 |
| libyaml (`yaml`) | 0.2.5 / hebe6cf0_3 | 82.95 | 0.353 |

The increment is **531,471 compressed bytes (519 KiB)** and **2,640,785
recorded regular-file bytes (2.52 MiB)**. Recorded file lengths include installed
bytecode, exclude symlinks/directories, Conda metadata and unrecorded later
imports, and count logical lengths rather than physical disk allocation.
Hard links, filesystem compression and shared caches affect physical usage.
Compressed package payload excludes channel indexes, network overhead and
retries. The two native create commands overlapped and each has only one wall
time observation; those observations do not establish installation latency or
an incremental solver/download time.

Published ArgDigest 0.14.0 does not require NumPy for the core route. Its Python
metadata places NumPy behind scientific extras, its Conda run dependencies omit
it, and neither installed records nor cold-import module inventories contain
NumPy. Core citations, independent reused captures, portable saved readers and
BibTeX reporting pass in this environment. PyYAML/libyaml still make the closure
partly native. The accepted four direct dependencies remain unchanged; a
scientific host can add its own NumPy or optional engine requirements.

Seven fresh-process timings and three separate Python-allocation samples per
case reuse `benchmark_lifecycle`: cold import has median **170.13 ms**, range
163.70–183.27 ms, with a 10.52 MiB median traced peak. First registration has
median 147.02 µs and first credit 22.27 µs. In the separate one-reference report
case, the first workflow report takes median 1.296 ms and a repeat 0.197 ms;
capture, tracking, snapshot, export and BibTeX stages remain separate in the
receipt. These processes start after smoke verification with warm filesystem
caches. This public runtime and its small distribution inventory differ from
the newer developer wheels and inherited environments in #115–#117. Comparing
their numbers does not establish an optimization effect or scientific speedup.

Reproduce with a new directory and a maintained MolSysSuite tools checkout:

```bash
STUDY_ROOT=$(mktemp -d)
CONDA_PKGS_DIRS="$STUDY_ROOT/python-cache" conda create --yes --json --no-default-packages --prefix "$STUDY_ROOT/python" --override-channels --strict-channel-priority -c uibcdf -c conda-forge python=3.14 > "$STUDY_ROOT/python-create.json"
CONDA_PKGS_DIRS="$STUDY_ROOT/public-cache" conda create --yes --json --no-default-packages --prefix "$STUDY_ROOT/public" --override-channels --strict-channel-priority -c uibcdf -c conda-forge python=3.14 ackredit=0.11.0=py_0 > "$STUDY_ROOT/public-create.json"
python /path/to/molsyssuite/devtools/scripts/verify_public_conda.py --package ackredit --version 0.11.0 --subdir noarch --filename ackredit-0.11.0-py_0.tar.bz2 --sha256 df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f --attempts 1 --output "$STUDY_ROOT/public-verification.json"
```

Require success at each step. Then, from outside the Ackredit checkout:

```bash
"$STUDY_ROOT/public/bin/python" /path/to/ackredit/devtools/benchmark_public_installation.py --control "$STUDY_ROOT/python" --delivery-receipt /path/to/ackredit/devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json --public-verification "$STUDY_ROOT/public-verification.json" --output "$STUDY_ROOT/receipt.json"
```

The output must be new. Keep both caches until measurement finishes: the tool
hashes the original archives, rejects nonpublic channels, verifies loaded
provider origins and versions, and checks recorded file lengths and tool hashes
again after sampling. It uses native Conda records, the shared verification
receipt, `installed_smoke` and `benchmark_lifecycle`; it does not introduce an
installer or a new release gate. Future solver results may select other builds.
The shared verifier source used here is MolSysSuite
`25363f2a2c902c04b2cdc8b301a3e1c1ff0c0918`.

This verifies a practical public receiving route with a bounded small increment
on one host. It is not an unconditional footprint target, another platform's
closure, third-party plugin workload, scientific equivalence check or new
release qualification. Roadmap L remains open.

## Normally installed plugin packs (2026-10-06)

[#117](https://github.com/uibcdf/ackredit/issues/117) adds
`devtools/benchmark_plugins.py`. The existing entry-point unit tests substitute
objects; this tool builds controlled citation/format packages with setuptools
and installs their original wheels normally. Fixtures are fictional registration
workloads, not third-party scientific libraries or published client adoption.
Each variant has a disposable environment with the same four normally installed
Ackredit/SMonitor/ArgDigest/DepDigest wheels and inherited Conda dependencies.
The Ackredit runtime remains the #116 candidate `45294c4`; this checkpoint changes
tooling/tests/evidence only. Other provider identities remain those recorded in
the raw receipt. This is local Linux/Python 3.14.7 evidence, not clean external
dependency closure or wider platform qualification.

The [raw installed receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/installed_plugins_117_2026-10-06.json)
retains original core/fixture wheel hashes and package-file maps, verified loaded
origins, actual entry points, tool hashes and 100 raw process samples: five variants,
seven timing and three separate allocation rounds, with cold and warm-operation
processes independent. Case order alternates. Build/install, verification and
the plugin-free reader are outside timing. This environment layout has its own
zero-pack control; do not infer a speedup by comparing its cold import with #116.

| Packs × references per pack | Cold import median (range), ms | Citation reload median, ms | First format discovery median, ms | Cold traced peak, MiB |
| --- | --- | --- | --- | --- |
| 0, one manually declared control | 130.94 (129.23–148.24) | 23.37 | 23.17 | 8.96 |
| 1 × 1 | 132.20 (130.82–148.76) | 23.86 | 23.39 | 8.96 |
| 10 × 1 | 136.03 (135.17–159.17) | 25.76 | 26.37 | 8.98 |
| 1 × 1,000 | 173.41 (170.82–201.97) | 65.29 | 24.16 | 9.11 |
| 10 × 100 | 169.77 (166.33–191.77) | 57.42 | 27.08 | 9.23 |

One to ten small packs has overlapping cold-import ranges. Registering 1,000
references is a larger cost in these fixtures, while format discovery depends
mostly on distribution scanning and format callback loading. Repeated discovery
has medians of 1.19–1.98 µs because format activation is already guarded once.
Those distinct stages must not be added to estimate a scientific workflow.

Two captures, each calling every pack's square function and retaining every
bound reference, take median 0.365 ms for one reference, 1.572 ms for ten,
and about 103.6–104.9 ms for 1,000. Snapshot work is included in that stage;
it is not a per-credit-loop benchmark. Workflow rendering after discovery takes
about 22.0 ms for 1,000 references. The custom ID renderer takes about 4.27–4.46 ms
for that size; the zero-pack control instead requests the built-in text renderer,
so its requested-report timing has a different renderer contract.

Every capture retains its own original bibliography and fixture-version note,
repeated reports are equal, and snapshots round-trip. A separate environment with
no plugin entry points restores the exact saved JSON, renders the workflow and
adds no execution credit. Actual installed guards cover broken citation/format
callbacks, a built-in name conflict, surviving neighbors, lazy/reentrant format
activation, repeated citation reload, a provider installed after import and a
fixture operation with Ackredit absent. No failures or skips are normalized away.

Reproduce with the four original runtime wheels and their `qualification_bundle`
records in `CORE_DIRECTORY/manifest.json`:

```bash
python devtools/benchmark_plugins.py --core-wheels CORE_DIRECTORY --destination NEW_DIRECTORY --samples 7 --memory-samples 3
```

The destination must be new; it retains fixture sources, original wheels, normal
environments, saved results and `receipt.json`. The standard build uses isolation;
`--no-build-isolation` selects a prepared build interpreter with setuptools>=64.
The tool reuses `benchmark_lifecycle` and `qualification_bundle`, rather than
introducing a separate timing or installed-file verification implementation.

The next reusable discovery/freshness decision is handed to
[DepDigest #31](https://github.com/uibcdf/depdigest/issues/31). A startup cache
cannot silently lose late-installed providers. This checkpoint does not implement
that proposal, alter public discovery timing or close roadmap L's dependency,
scientific-workload, graph-shape and platform criteria.

## Startup discovery and deferred imports (2026-10-06)

[#116](https://github.com/uibcdf/ackredit/issues/116) separates format discovery
from rendering using `--startup-only`. Five cases run with nine timing and
three separate allocation samples each, before and after delaying network
support until DOI fetching and process support until PDF compilation. Both
developer wheels are normally installed at the same path, with the same four
provider wheels. Every shipped file is verified; the other 322 distribution
versions and entry-point text digests match. Sources are the #115 runtime
baseline `b8f7100` and candidate `45294c4`.

The [baseline samples](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/startup_before_116_2026-10-06.json),
[candidate samples](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/startup_after_116_2026-10-06.json)
and [installation evidence](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/startup_installed_116_2026-10-06.json)
retain 120 raw samples and original wheel identities. Cohorts run sequentially,
baseline then candidate, without concurrent task builds/tests. This local
Linux/Python 3.14.7 lane inherits the maintained Conda dependencies; it is not
a clean public installation or release qualification.

| Stage | Baseline median (range), ms | Candidate median (range), ms |
| --- | --- | --- |
| Cold import, including citation discovery | 161.86 (148.53–194.88) | 160.48 (149.04–172.85) |
| First workflow report, one reference | 25.82 (24.24–27.47) | 24.77 (23.32–28.52) |
| Explicit format discovery, one reference | 25.91 (24.05–26.42) | 24.34 (23.09–26.98) |
| Workflow after explicit discovery, one reference | 0.290 (0.229–0.413) | 0.248 (0.219–0.338) |
| Repeated workflow, one reference | 0.162 (0.141–0.192) | 0.148 (0.138–0.226) |
| First workflow report, 1,000 references | 51.75 (49.26–53.26) | 49.36 (48.40–50.97) |
| Workflow after explicit discovery, 1,000 references | 25.96 (25.20–26.77) | 24.24 (23.19–25.96) |

Cold-import traced Python allocation peak falls from 10.68 to 8.95 MiB;
retained allocations fall from 10.41 to 8.68 MiB. Successful offline operations
in this fixed environment no longer load `urllib.request`, `ssl` or `subprocess`.
The imports move to the features that need them, so first network/PDF use still
pays their initialization. Latency ranges overlap: these samples do not establish
a reliable cold-import speedup or a report-rendering optimization.

The [exploratory profile](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/startup_profile_116_2026-10-06.json)
locates the dominant one-reference first-report work in standard-library
`importlib.metadata.entry_points`: the scan reads distribution entry-point text
even when no Ackredit plugins are installed. Its instrumented cumulative times
overlap and must not be added or used as latency estimates. With 1,000 references,
rendering itself also matters. Repeated reports are checked for exact equality;
journals, snapshots, argument validation and plugin lifecycle stay intact.

Citation discovery still runs on import and explicit `load_plugins()` calls;
format discovery still runs on first demand, with its reentry guard. A shared
startup cache would change late-provider discovery unless it has a separate
invalidation contract. DepDigest's inspected `LazyRegistry` delegates to the
same standard-library enumeration and adds module-registry behavior, so it is
not an equivalent faster replacement for Ackredit's registration callbacks.
Investigate real plugin packs and an owned reusable discovery contract before
changing that boundary. Broader dependency closure, graph shapes and platform
qualification remain roadmap L work.

```bash
python devtools/benchmark_lifecycle.py --startup-only --samples 9 --memory-samples 3 --output startup.json
```

## Installed development follow-up (2026-10-06)

The repeat under [#115](https://github.com/uibcdf/ackredit/issues/115) selects
clean SMonitor `6feac97` and ArgDigest `5e7925d`, after their scoped-diagnostics
changes. Ackredit `b8f7100`, DepDigest `0568f9a` and PyUnitWizard `2ab37a5`
are also built once from clean temporary clones and normally installed as
development wheels. Runtime and distribution versions now agree, and the
existing receiving verifier checks every shipped file against its original
wheel. See the [installation receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/lifecycle_installed_115_2026-10-06.json).
The original checkouts are unchanged. This is Linux/Python 3.14.7 with scientific
dependencies inherited from the maintained Conda environment, not a clean public
Conda installation, a release or complete supported-platform qualification.

The [follow-up samples](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/lifecycle_followup_115_2026-10-06.json)
retain 34 cases, seven timing and three separate allocation samples each.
The original 24 cases are joined by ten explicitly requested metadata-only
scientific cases. Actual package fingerprints remain fixed throughout. Every
final output element, unit and credited version passes the same guards; all
scientific modes produce the same value digest for their input size. Journals
and snapshots still round-trip, and all worker stderr fields are empty.

Cold import has median 173.26 ms and range 151.22–191.88 ms, with a peak of
10.69 MiB of traced Python allocations. First registration and first plain
credit have medians 120.28 and 18.78 µs. Activation of a 1,000-function/reference
provider takes 27.54 ms. With 1,000 unique references, a snapshot takes 20.21 ms,
JSON export 2.38 ms and the first requested workflow report 49.16 ms. Journal
tracking takes 75.34 ms, excluding its separately measured open/close and reports.
These stages identify where to profile next. Their comparison with the earlier
temporary-source snapshot changes source versions and installation layout;
it is not an isolated before/after measurement of either dependency's speedup.

SMonitor's metadata-only policy is entered explicitly around the scientific
calls. Scope entry/exit and warm-up remain outside the timed loops. ArgDigest's
new independent selection remains at its compatible default: Ackredit still
runs its argument digesters, signature rules and refusal contracts. No public
validation is bypassed. Microseconds per conversion below show median and range;
each cell compares ordinary diagnostics with the explicitly restricted scope.

| Conversion | One value: ordinary / metadata-only | 100,000 values: ordinary / metadata-only |
| --- | --- | --- |
| Unattributed control | 48.13 (46.52–55.49) / 59.79 (56.70–68.60) | 125.23 (123.17–126.92) / 127.56 (126.91–133.94) |
| Backend attribution | 78.07 (74.68–94.65) / 88.35 (85.68–93.63) | 151.23 (145.99–156.48) / 158.36 (155.05–168.74) |
| Public observation and backend | 95.27 (94.54–110.19) / 104.67 (101.06–109.60) | 172.14 (163.94–177.79) / 185.86 (176.98–225.40) |
| Observation inside a result capture | 100.81 (98.00–111.60) / 110.20 (106.13–114.92) | 171.64 (166.20–181.01) / 183.83 (175.66–200.77) |
| Capture with recorder evidence | 103.26 (102.51–120.00) / 115.37 (110.31–123.89) | 174.12 (171.51–178.63) / 187.95 (184.27–191.65) |

The restricted scope adds about 9.4 and 12.2 µs to the captured conversion
medians for these two sizes. Successful calls here do not format failure
payloads, so this study cannot establish savings on error-heavy workflows.
The policy restricts SMonitor/ArgDigest-owned diagnostic collection; original
scientific bibliography and recorder evidence remain available. These successful
workloads do not prove a general provider redaction contract.

The unchanged portable tool has its
[own follow-up receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/lifecycle_portable_followup_115_2026-10-06.json).
Its medians include 0.085 µs for the unobserved synthetic function, 7.46 µs
with observation and 2.85 µs for a prepared credit inside a capture. Those
warmed figures exclude import, activation and first use.

```bash
python devtools/benchmark_lifecycle.py --scientific --scoped-diagnostics --samples 7 --memory-samples 3 --output lifecycle.json
```

`--scoped-diagnostics` requires the scientific cases and SMonitor's actual
scope capability; it never silently substitutes ordinary diagnostics. This
completes the first #115 measurement checkpoint. Next profiling should separate
first-report format-plugin discovery from warmed rendering and investigate cold
initialization in its owning modules. Plugin packs, independent graph shapes,
external installed dependency closure and the wider platform matrix remain
roadmap L work.

## Provisional lifecycle reference (2026-10-06)

The installed follow-up above supersedes this snapshot as the current reference.
Its original samples and limits remain historical evidence.

[Ackredit #115](https://github.com/uibcdf/ackredit/issues/115) adds a bounded
Linux/Python 3.14.7 study. It remains provisional while SMonitor development is
in progress. Seven timing samples and three separate allocation samples run
in fresh interpreters and independent directories for each of 24 cases.
Cold import starts before the benchmark's metadata/reporting imports; timings
do not run under tracemalloc. Scenario order reverses on alternate rounds.

The [raw receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/lifecycle_cost_115_2026-10-06.json)
records actual origins, runtime and distribution versions, package source
fingerprints, all samples, ranges and output dimensions. A
[source manifest](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/lifecycle_sources_115_2026-10-06.json)
records every copied file and the original checkout states. Ackredit source
is based on `0e077a9`; five development packages were copied to a fixed temporary
directory to preserve concurrent work. These are source measurements, not a
normal installation or public release qualification. SMonitor's copied runtime
version is `0.18.0+38.g677dc0f.dirty`, while its installed distribution metadata
still says `0.18.0+37.g6cdba4d`. The tool keeps those facts separate and rejects
changing loaded source fingerprints, even if a version string stays constant.
Exact snapshot reconstruction requires the recorded working files; the original
Git heads alone do not contain those uncommitted provider changes.

| Separate stage | Median | Observed range |
| --- | ---: | ---: |
| Cold Ackredit import | 189.14 ms | 161.66–344.10 ms |
| First reference registration | 150.95 µs | 118.58–162.18 µs |
| First plain credit | 21.73 µs | 19.00–25.07 µs |
| Provider activation, one reference/function | 186.81 µs | 174.31–200.36 µs |
| Provider activation, 1,000 references/functions | 29.65 ms | 26.81–35.86 ms |
| First workflow report, one reference | 26.67 ms | 24.63–28.47 ms |

Import has a large outlier, retained in the range. Python allocation peaks for
import and the 1,000-function activation are respectively 10.64 MiB and
3.12 MiB. These allocation figures exclude interpreter startup, native buffers,
RSS and installed dependency size. Activation excludes creation of the producer's
input declaration. No installed citation plugin packs were present, and NumPy
was absent from the modules loaded by cold Ackredit import in this snapshot.
ArgDigest declares NumPy through optional extras here; that does not establish
the dependency closure of the lowest supported or currently published artifact.

Scaling cases retain one reference per leaf, with a shared root: 1,000 references
mean 1,001 nodes and 1,000 edges. Medians for that case are 54.62 ms for unique
tracking, 22.32 ms for a detached snapshot, 2.49 ms for JSON export, 52.59 ms
for the first requested workflow report and 12.22 ms for the subsequent BibTeX
report. The first report includes format-plugin discovery; the following
BibTeX stage does not repeat that initialization. These are complete stage
times, not per-call costs or equivalent warmed renderer comparisons.

Tracking 100 references in one, four and sixteen active captures takes 5.77,
8.54 and 20.00 ms, with peak extra Python allocations of 427, 819 and 2,396 KiB.
All captures retain the full independent bibliography. Keeping 100 independent
one-reference results takes 11.02 ms and retains approximately 279 KiB of
additional traced allocations. Journal-enabled tracking of 1,000 unique
reference/graph updates takes 75.94 ms; journal open and close are separately
0.34 and 2.68 ms. Snapshot/export/report stages are excluded from those journal
figures, and every journal passes a retained-state round trip.

Real controls use PyUnitWizard `0.28.1+3.g2ab37a5`, Pint 0.25.3, unyt 3.1.0 and
NumPy 2.4.6. Pint converts meter arrays to centimeters; the study asserts every
value, output unit and original credited version outside the timed region.
Within each input size, every mode and sample produces the same value digest.
Imports, activation, input creation and the warm-up call are excluded. Values
below are microseconds per conversion: median followed by minimum–maximum.

| Warmed real conversion | One value | 100,000 values |
| --- | ---: | ---: |
| Ordinary control | 50.58 (47.47–56.06) | 127.88 (120.71–146.26) |
| Completed-backend attribution | 81.80 (80.10–91.35) | 157.29 (151.86–168.86) |
| Backend and public-function observation | 101.40 (95.30–108.89) | 184.81 (166.74–214.54) |
| Observation inside a result capture | 106.74 (100.88–108.19) | 184.22 (172.41–201.22) |
| Capture with explicit recorder evidence | 113.05 (107.03–124.08) | 192.01 (180.86–216.39) |

Backend attribution credits Pint; public observation additionally credits
PyUnitWizard. Ordinary variation remains visible, and overlapping ranges do
not establish that adding capture makes a computation faster. These costs do
not combine with historical speedup percentages elsewhere on this page.

Re-run the protocol with fixed package sources in the selected environment:

```bash
python devtools/benchmark_lifecycle.py --scientific --samples 7 --memory-samples 3 --output lifecycle.json
python devtools/benchmark_portable.py --samples 7 --iterations 5000
```

The scientific option requires the real producer and engines and never skips
an unavailable dependency. Separate unobserved/prepared-credit timings remain
the portable tool's responsibility. In the same fixed-source environment,
its seven-sample medians are 0.12 µs for the unobserved synthetic function,
8.68 µs with active observation, 2.00 µs for a prepared credit and 3.10 µs
for a prepared credit inside a capture. The
[separate raw receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/lifecycle_portable_115_2026-10-06.json)
retains all warmed samples; these exclude activation, import and first credit.
The next #115 checkpoint repeats the
affected cases against the final selected SMonitor source before choosing an
optimization. Real plugin-pack initialization, independent graph shapes,
clean installed dependency closure and other platforms remain roadmap L work.

## One instrumented call

This is the number that scales, and the one to reach for when deciding what to instrument.

| | |
| --- | --- |
| `track_item(...)` | **1.2 µs** |
| `scope(...)` with a `track_item` inside | **4.5 µs** |

Both rose by about 0.15 µs when `uibcdf/ackredit#62` adopted ArgDigest. The tracking path
is deliberately **not** decorated — the decorator costs 11.7 µs, which would be ten times
the call — and checks its argument inline instead, which is what that difference is.

A function you instrument costs that much per call. Instrumenting something called a
thousand times a second costs four milliseconds of that second; instrumenting an inner loop
that runs ten million times costs forty seconds, and should not be instrumented — bind the
citation to the function that calls it instead, which is what
{func}`ackredit.bind` is for.

## Portable capture and declared function calls (2026-10-04)

The historical plain-path figures above do not measure portable capture. The
new `devtools/benchmark_portable.py` separates those costs on Linux/Python
3.14.7. Each scenario uses 15 samples and 5,000 repeated credits; snapshots and
renders use 100 operations. Values below are medians in microseconds for one
reference, with a small bibliography and context. Baseline source is unchanged
`148ffb4`; optimized development files and all samples are fingerprinted in
[`portable_capture_85_2026-10-04.json`](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/portable_capture_85_2026-10-04.json).

| Operation | Previous code (two trials) | Optimized development |
| --- | ---: | ---: |
| Plain `track_item` | 1.41–1.58 | 1.42 |
| Contextual `track_item` | 47.84–53.67 | 39.47 |
| Repeated credit inside a capture | 61.91–67.20 | 41.32 |
| Repeated credit inside two nested captures | 73.70–80.77 | 43.81 |
| Unobserved provider function | — | 0.08 |
| Declared provider function, active observation | — | 8.05 |
| Declared provider function, one capture | — | 10.40 |
| Declared provider function, nested captures | — | 12.24 |

The ordinary captured credit is about **33–39% cheaper** in these trials;
nested capture about **41–46% cheaper**. The unchanged plain path also drifted
between trials, so these are bounded observations, not exact speedup promises.
Each trial's spread and all raw samples are retained. Snapshot and BibTeX
differences are not claimed as improvements: their medians are about 124 µs
and 212 µs here, and runtime variation affects them too.

Capture avoids copying retained records again and shares one normalized use
key across its builders. Public inputs still receive JSON validation and
detachment on every call. The provisional function provider validates and
detaches declarations at activation, prepares contextual keys once, and uses
the same capture/session writers on every actual entry. It still checks
registered bibliographic contents and captured identity conflicts. A fresh
capture receives reused references; mutable input identity is never a cache key.

When observation is off, the provider is the original function with no Ackredit
wrapper. The active measurements include its tiny example computation and one
citation; they are total call times, not incremental overhead subtracted from a
scientific pipeline. Imports, activation, first-credit setup and capture entry/
exit are excluded. More references and bigger contexts cost more. This is not
evidence that arbitrary scientific workloads are free to instrument, or that
the feature is already in public Ackredit 0.9.0. The scientific-workflow results
below remain their own historical measurement.

```bash
python devtools/benchmark_portable.py --samples 15 --iterations 5000
```

## Real PyUnitWizard dispatch (development pilot, 2026-10-04)

PyUnitWizard #94 measures a warmed Pint conversion with backend attribution
and the provisional public-function observer. Seven raw samples and source
SHA-256 values are preserved in its
[before receipt](https://github.com/uibcdf/pyunitwizard/blob/main/devtools/receipts/function_provider_94_before_2026-10-04.json)
and [after receipt](https://github.com/uibcdf/pyunitwizard/blob/main/devtools/receipts/function_provider_94_2026-10-04.json).
Linux/Python 3.14.7 medians, in microseconds per conversion:

| Warmed operation | One value before / after | 100,000 values before / after |
| --- | ---: | ---: |
| Ordinary conversion, attribution disabled | 48.95 / 47.33 | 119.67 / 112.30 |
| Backend references in a result capture | 272.34 / 96.75 | 338.81 / 165.85 |
| Public function and backend references in a capture | 302.02 / 114.79 | 379.25 / 183.55 |

The host prepares fixed backend credits once using provisional `prepare_credit`
(#87), retaining per-use registry comparison and every current capture/session
write. It keeps the released public tracking fallback when that capability is
absent. Numerical results, original versions, software/article roles, pipeline
parentage and bibliography-replacement diagnostics are guarded by the real
receiver tests.

Small captured conversions are about 64% cheaper in this local before/after
measurement, or 62% with public-function observation included. Ordinary timings
also drift; these are bounded total-time measurements, not universal speedups.
Imports, initial registration/preparation and activation are excluded. Optimized
backend capture still adds about 49 µs to the ordinary small conversion;
combined function/backend capture adds about 67 µs. A heavy array does not add
one credit per element. This development improvement is absent from public
0.9.0 and does not qualify a client release.

## Repeated writer allocations (development, 2026-10-05)

[Ackredit #97](https://github.com/uibcdf/ackredit/issues/97) avoids constructing
temporary graph nodes for targets already retained, and retains each normalized
use once per builder. Every invocation still checks registered bibliography and
all active builders for conflicts. Independent captures receive their own uses;
an existing target can still acquire another parent. Public inputs retain their
validation and detachment, and journal changes use the same locked writer.

Both versions are normally installed outside their checkouts on Linux/Python
3.14.7. Original Ackredit is `cfb5140`; candidate runtime files, exact dependency
versions and every sample are retained in
[the receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/repeated_attribution_97_2026-10-05.json).
The existing portable benchmark now includes explicit prepared credits. Its
15-sample medians, in microseconds per warmed operation, are:

| Operation | Original | Candidate |
| --- | ---: | ---: |
| Plain credit | 1.44 | 1.18 |
| Prepared credit | 2.57 | 1.65 |
| Prepared credit, one capture | 4.25 | 2.59 |
| Prepared credit, two nested captures | 5.85 | 3.53 |
| Declared function, one capture | 11.10 | 8.00 |
| Declared function, two nested captures | 13.12 | 9.18 |
| Public contextual credit, one capture | 42.88 | 39.80 |

The prepared captured writer is about 39% cheaper in this bounded trial.
Public contextual tracking improves less because normalization still occurs
on every call. Snapshot and BibTeX medians remain approximately 128 and 227 µs;
no report-speed improvement is claimed here. Imports, activation, preparation
and capture entry/exit are excluded from repeated-call timings.

The unchanged PyUnitWizard benchmark is also run in three independent process
pairs, alternating order, with seven samples per case. Both installations use
PyUnitWizard `2d12b37`, Pint 0.26.1, unyt 3.1.0 and NumPy 2.5.3. Ranges of
the three trial medians, in microseconds per conversion:

| Real conversion | One value, original / candidate | 100,000 values, original / candidate |
| --- | ---: | ---: |
| Ordinary | 42.87–45.68 / 44.38–44.42 | 108.00–112.62 / 108.44–109.77 |
| Backend capture | 86.63–90.72 / 84.00–85.16 | 150.62–157.32 / 147.29–150.16 |
| Function and backend capture | 106.22–111.25 / 101.10–102.52 | 169.71–184.35 / 165.16–169.28 |

These are total scientific conversion times with ordinary-control drift, not a
universal speedup or a hosted release qualification. Four unchanged installed
receiving guards pass for each version: Pint/unyt numerical results, independent
captures, original software/article references and versions, graph parentage,
entry versus completion, optional absence and producer/network-blocked saved
workflow reading. The remaining producer-owned declaration copies are reported
in [PyUnitWizard #111](https://github.com/uibcdf/pyunitwizard/issues/111).
No new dependency, portable schema or provisional API decision follows.

## Requested provenance reports (2026-10-04)

Ackredit #91 removes repeated expansion of shared graph descendants and
recursive traversal. `devtools/benchmark_provenance.py` compares the unchanged
renderer at `136b5d6` with the development repair, using 15 samples of 50
warmed renders per case on Linux/Python 3.14.7. It retains individual samples,
source hashes and scope in
[the raw receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/provenance_graph_91_2026-10-04.json).

| Graph (20 nodes) | Median before / after, µs | Output lines before / after |
| --- | ---: | ---: |
| Ordinary chain, 19 edges | 55.72 / 40.61 | 22 / 22 |
| Shared branches, 36 edges | 4,670.32 / 52.14 | 2,048 / 40 |

Each target now expands once, while every incoming edge remains visible;
references to an already shown shared node and ancestor cycles have different
markers. Valid deep graphs no longer use Python recursion. Structural visits
are bounded by stored nodes and edges; sorting and output indentation still
depend on graph shape and text size. These synthetic report-only timings
exclude import, graph construction and capture. They do not measure a faster
scientific calculation or tracking path, and the repair is absent from public
0.9.0.

## A real workflow (historical measurement)

MolSysMT reading a protein from the PDB, converting it, querying it, selecting from it and
converting it again. Roughly four seconds of real work, instrumented the way
`standards/ACKREDIT_GUIDE.md` describes.

```
  no Ackredit                         4.0787 s
  its own spread over 7 runs           259.4 ms
  tracked, as the guide describes     4.0559 s      -22.8 ms    -0.56%   under the noise
  tracked, with persistence           3.9732 s     -105.5 ms    -2.59%   under the noise
```

**There is no number to give here, and that is the finding.** The workflow's own run-to-run
spread is 259 ms, and every difference Ackredit makes is smaller than that — in this run
both came out *negative*, which is how you can tell you are looking at noise rather than at
a cost. Twenty instrumented calls at four microseconds is eighty microseconds against four
seconds; it does not show, and no honest measurement will make it show.

## Auto-discovery

`ackredit.enable_import_hooks()` watches imports and credits the packages it can identify.
That one is measurable.

```
  import molsysmt                     0.2966 s
  its own spread over 7 runs            11.2 ms
  import molsysmt, hooks enabled      0.3181 s      +21.6 ms    +7.28%
```

**Fifteen to twenty milliseconds**, once, for a library that pulls in eighteen packages
Ackredit can credit. It is paid at import and never again.

The range is the honest form of it. On a quiet machine the baseline's spread is 11 ms and
the difference stands clear of it; on a busy one the spread reaches 28 ms and the same
difference sits inside. So it is real and it is small — small enough that whether a single
run can separate it depends on the machine, which is why the table prints the spread beside
the number.

## Persistence

Enabling a journal costs 0.13 ms, closing it 2.5 ms — that is the single `fsync` that makes
what was written durable. Between them, each tracked event is one appended line, and the
cost does not grow with how many came before: `tests/test_persistence_cost.py` holds it to
that.

## What these numbers do not say

These historical measurements cover one machine, one workload and one day.
They do not establish cost on another host, input, provider or environment.
Cold imports, initialization, retained results and requested reports have
separate costs; measure the stages your application actually uses.

If your run is different — an inner loop instrumented, a session with a hundred thousand
items — measure it. The script takes the workload as its first few lines and the rest of it
is method: minimum of several runs, each in its own interpreter, and both sides importing
Ackredit so the only difference is whether the feature is on.

```bash
python devtools/benchmark.py
```

It needs MolSysMT, which is not a dependency of Ackredit, and says so if it is absent.

Each persistence repetition owns a managed temporary directory. Its writer closes
before that directory is removed, on success and on failure; cleanup failures
remain visible. Directory setup and writer closure/removal are outside the timed
region. These lifecycle checks use synthetic test inputs and do not repeat the
historical MolSysMT measurements ([Ackredit #130](https://github.com/uibcdf/ackredit/issues/130)).
