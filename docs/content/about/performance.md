(About_Performance)=
# What Ackredit costs

Numbers, not adjectives. They come from `devtools/benchmark.py`, which you can run.

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

They are one machine, one workload, one day. What is stable across machines is the shape:
the per-call cost is microseconds, the workflow cost is invisible beneath ordinary
variance, and auto-discovery is a one-off at import.

If your run is different — an inner loop instrumented, a session with a hundred thousand
items — measure it. The script takes the workload as its first few lines and the rest of it
is method: minimum of several runs, each in its own interpreter, and both sides importing
Ackredit so the only difference is whether the feature is on.

```bash
python devtools/benchmark.py
```

It needs MolSysMT, which is not a dependency of Ackredit, and says so if it is absent.
