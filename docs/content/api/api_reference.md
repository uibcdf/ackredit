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

## Portable attribution (reviewed contract)

`capture(name, context=...)` observes one calculation alongside the current
session. Its `attribution` property returns an `Attribution` snapshot;
`get_attribution()` snapshots the enclosing workflow. `Attribution.from_dict`
and `from_json` read saved bibliography without new credit; `to_dict` and
`to_json` detach it, and `report` renders the original records. Contextual
`track_item(..., roles=[...], context={...})` associates papers with software
versions without adding role fields to bibliographic records.

See [the canonical integration guide](https://github.com/uibcdf/ackredit/blob/main/standards/ACKREDIT_GUIDE.md)
for the schema and failure behavior, and the
[portable compatibility contract](../user_guide/portable_attribution.md) for
the public 0.9.0 delivery boundary.

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

`observe_calls(*modules)` is a provisional, opt-in context for observing actual
calls to declared direct function exports of already imported modules. Its
[third-party provider guide](../user_guide/function_providers.md) specifies
dependency-free declarations, citation roles, restoration and observation limits.
It is development functionality; public Ackredit 0.9.0 does not include it.

`prepare_credit(item_id, used_by, *, roles=(), context=None)` provisionally
prepares a fixed contextual use of an already registered reference and returns
an explicit credit callable. The host invokes it when scientific dispatch
earns that reference; it creates no call scope or automatic observation.
The same [provider guide](../user_guide/function_providers.md) documents its
detachment, current-capture behavior and replacement diagnostics. Public 0.9.0
does not expose it; its owning review is Ackredit #87.

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
