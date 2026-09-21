(User_Tracking)=
# Tracking Usage

Ackredit allows you to track usage at different levels of granularity, from whole functions to specific blocks of code.

## Using Decorators
The {func}`ackredit.scoped_usage` decorator is the easiest way to track when a function is called.

```python
import ackredit


@ackredit.scoped_usage("my_library.analysis")
def run_analysis():
    # This automatically marks 'my_library.analysis' as used
    pass
```

### Crediting bound items automatically

`bind` declares which items a target *may* require. By default those declarations
are inert at runtime, so that only what a code path actually reached is reported.
When a function's citations do not depend on the path taken, opt in with
`credit_bound=True`:

```python
import ackredit

ackredit.register_item(id="paper:base", type="article", title="Base method")
ackredit.bind("my_library.analysis", ["paper:base"])


@ackredit.scoped_usage("my_library.analysis", credit_bound=True)
def run_analysis(mode="basic"):
    # 'paper:base' is credited on every call
    if mode == "advanced":
        ackredit.track_item("paper:advanced")
```

Read declarations back at any time with {func}`ackredit.bound_items`, or apply them
explicitly with {func}`ackredit.credit_bound`.

:::{seealso}
{ref}`User_Registration` explains how items and bindings are declared in the first
place, and {ref}`User_Reporting` covers turning what was tracked into a citation
report.
:::

## Using Context Managers
For more granular tracking within a function, use the {class}`ackredit.scope` context manager.

```python
import ackredit


def run_analysis():
    with ackredit.scope("data_loading"):
        # Marks 'data_loading' as a sub-scope
        ackredit.track_item("dataset:1")
```

### Sessions

Everything tracked belongs to a session. There is one by default, so nothing above needs
any ceremony. Where two things in one process want their own answer — cells in a
notebook, a host library keeping its tracking apart from its user's, two analyses
reported separately — enter one:

```python
import ackredit

with ackredit.session("first analysis") as run:
    analyse(dataset)
    first = ackredit.report()

with ackredit.session("second analysis"):
    analyse(other_dataset)
    second = ackredit.report()
```

Each report describes only its own block, and what was tracked outside is untouched.
Pass `inherit=True` to start from what the enclosing session already holds.

Declarations are not scoped this way on purpose. {func}`ackredit.register_item` and
{func}`ackredit.bind` say what *could* be cited, which a host library states once at
import; a session records what *was* used.

Entering a session is context-local, so a thread or asyncio task that does not enter one
keeps recording where it was — the same rule as {class}`ackredit.scope`.

### Concurrency

Scopes are context-local: each thread, and each asyncio task, keeps its own current
scope. Parallel workflows can therefore track independently without crossing
attribution, and no scope leaks to whatever runs next in a reused worker.

```python
from concurrent.futures import ThreadPoolExecutor


def analyse(case):
    with ackredit.scope(f"case_{case}"):
        ackredit.track_item("dataset:reference")


with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(analyse, range(8)))
```

Session persistence is safe under the same conditions: the file is written atomically, so
a concurrent reader or an interrupted run never sees a half-written document.

### Parallel processes

Threads share one collector. Separate processes do not, but the session file is a
journal that is appended to, so several may write the same one without losing events.
That guarantee comes from the operating system and holds on a local filesystem; a network
filesystem such as NFS does not provide it, so on a cluster give every process its own
journal and merge them at the end:

```python
import os

import ackredit

ackredit.enable_persistence(f"citations/session_{os.getpid()}.json")
```

```python
from glob import glob

import ackredit

ackredit.aggregate(glob("citations/session_*.json"))
print(ackredit.report())
```

The same merge is available from the command line with `ackredit merge`, and merging
journals is concatenation, so it costs nothing to do at the end of a large run.

Call `ackredit.close_persistence()` when the run finishes. Each event is already flushed
when it is recorded, so nothing is lost if the process dies; closing pays the single
`fsync` that makes the journal durable against the machine failing as well.

### Detecting what a function needs from its own source

When a function's citations follow from the calls it makes,
{func}`ackredit.auto_track_calls` reads its source once and credits the matching items
whenever it runs:

```python
import ackredit


def convert(item, to_form):
    mdtraj_load(item)


convert = ackredit.auto_track_calls(convert, {"mdtraj_load": "external:mdtraj"})
```

Nothing is credited until `convert` is called. The source only decides *what* would be
cited; running the function decides *whether*.

:::{note}
Detection is per function, not per branch. A function that runs but takes a path that
never reaches the detected call is credited anyway — the same coarseness as
`credit_bound=True`. Where the citations depend on the path taken, call
{func}`ackredit.track_item` on the branch that needs them.

A function whose source cannot be read, such as one defined in a REPL or provided by a C
extension, is returned unchanged and reports `ACKREDIT-W010`.
:::

## Manual Tracking
You can manually track any item at any point in your code.

```python
import ackredit


def compute():
    # Perform algorithm...
    ackredit.track_item("algorithm:paper:2015")
```

## Automatic Discovery (Import Hooks)
Ackredit can automatically track citations for third-party libraries when they are imported. This feature must be explicitly enabled.

```python
import ackredit

# Enable the magic
ackredit.enable_import_hooks()

# Now, importing common libraries will trigger their built-in citations
import numpy
import scipy
```
*Ackredit will look for: internal standard injections, `CITATION.cff` files in the library folder, and package metadata.*
