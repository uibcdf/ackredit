(About_Performance)=
# What Ackredit costs

Numbers, not adjectives. They come from `devtools/benchmark.py`, which you can run.

## One instrumented call

This is the number that scales, and the one to reach for when deciding what to instrument.

| | |
| --- | --- |
| `track_item(...)` | **1.0 µs** |
| `scope(...)` with a `track_item` inside | **4.1 µs** |

A function you instrument costs that much per call. Instrumenting something called a
thousand times a second costs four milliseconds of that second; instrumenting an inner loop
that runs ten million times costs forty seconds, and should not be instrumented — bind the
citation to the function that calls it instead, which is what
{func}`ackredit.bind` is for.

## A real workflow

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

About **20 ms**, once, for a library that pulls in eighteen packages Ackredit can credit.
The spread of that measurement is 11 ms, so unlike the workflow above this is a real
difference and not noise. It is paid at import and never again.

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
