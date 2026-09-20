# Tracking Usage

FlowCite allows you to track usage at different levels of granularity, from whole functions to specific blocks of code.

## Using Decorators
The `@scoped_usage` decorator is the easiest way to track when a function is called.

```python
import flowcite


@flowcite.scoped_usage("my_library.analysis")
def run_analysis():
    # This automatically marks 'my_library.analysis' as used
    pass
```

## Using Context Managers
For more granular tracking within a function, use the `scope` context manager.

```python
import flowcite


def run_analysis():
    with flowcite.scope("data_loading"):
        # Marks 'data_loading' as a sub-scope
        flowcite.track_item("dataset:1")
```

## Manual Tracking
You can manually track any item at any point in your code.

```python
import flowcite


def compute():
    # Perform algorithm...
    flowcite.track_item("algorithm:paper:2015")
```

## Automatic Discovery (Import Hooks)
FlowCite can automatically track citations for third-party libraries when they are imported. This feature must be explicitly enabled.

```python
import flowcite

# Enable the magic
flowcite.enable_import_hooks()

# Now, importing common libraries will trigger their built-in citations
import numpy
import scipy
```
*FlowCite will look for: internal standard injections, `CITATION.cff` files in the library folder, and package metadata.*
