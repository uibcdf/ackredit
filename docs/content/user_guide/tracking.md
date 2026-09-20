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
