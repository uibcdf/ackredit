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
