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

`observe_calls(*modules)` is an opt-in context for observing actual
calls to declared direct function exports of already imported modules. Its
[third-party provider guide](../user_guide/function_providers.md) specifies
dependency-free declarations, citation roles, restoration and observation limits.
Its bounded stable promise starts at public 0.11.0; public 0.9.0 does not include it.

`prepare_credit(item_id, used_by, *, roles=(), context=None)`
prepares a fixed contextual use of an already registered reference and returns
an explicit credit callable. The host invokes it when scientific dispatch
earns that reference; it creates no call scope or automatic observation.
The same [provider guide](../user_guide/function_providers.md) documents its
detachment, current-capture behavior and replacement diagnostics. Public 0.9.0
does not expose it; public 0.11.0 delivers its bounded stable promise under #87.

`validate_provider(module) -> dict` is a provisional standalone preflight added
in development after 0.11.0 under Ackredit #111. It returns a detached normalized
declaration using the observer's parser, without credit, bibliography
registration or Ackredit wrappers. The same provider guide specifies explicit
lazy-export resolution, catalog refusals and validation limits.

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
