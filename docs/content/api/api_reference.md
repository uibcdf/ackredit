(API_Reference)=
# API Reference

This page provides an overview of the Ackredit public API.

## Main Module

```{eval-rst}
.. automodule:: ackredit
   :members:
   :undoc-members:
   :show-inheritance:
```

## Portable attribution (provisional)

`capture(name, context=...)` observes one calculation alongside the current
session. Its `attribution` property returns an `Attribution` snapshot;
`get_attribution()` snapshots the enclosing workflow. `Attribution.from_dict`
and `from_json` read saved bibliography without new credit; `to_dict` and
`to_json` detach it, and `report` renders the original records. Contextual
`track_item(..., roles=[...], context={...})` associates papers with software
versions without adding role fields to bibliographic records.

See [the canonical integration guide](https://github.com/uibcdf/ackredit/blob/main/standards/ACKREDIT_GUIDE.md)
for the schema, failure behavior and development-only adoption status.

```{eval-rst}
.. automodule:: ackredit.core.attribution
   :members: Attribution, capture, get_attribution
```

## Core Components

These are internals, documented for anyone working on Ackredit. They are not part of the
public surface: `Registry` and `Collector` are reached through `register_item`,
`bound_items` and `get_used_items`, and what Ackredit promises is in
{ref}`API stability <About_Stability>`.

### Registry
```{eval-rst}
.. automodule:: ackredit.core.registry
   :members:
   :undoc-members:
```

### Collector
```{eval-rst}
.. automodule:: ackredit.core.collector
   :members:
   :undoc-members:
```

### Report & Dump
```{eval-rst}
.. automodule:: ackredit.core.report
   :members:
   :undoc-members:
```

## Decorators & Context
```{eval-rst}
.. automodule:: ackredit.core.decorators
   :members:
   :undoc-members:
```

```{eval-rst}
.. automodule:: ackredit.core.context
   :members:
   :undoc-members:
```
