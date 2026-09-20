# Developer notes

A one-screen reminder of the shapes Ackredit is expected to have. The authoritative
texts are [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) for using the library and
[`standards/ACKREDIT_GUIDE.md`](standards/ACKREDIT_GUIDE.md) for embedding it in a host
library; keep those correct first.

## Flat public API

```python
import ackredit

ackredit.register_item(id="paper:2024", type="article", title="A paper")
ackredit.bind("mylib.run", ["paper:2024"])
ackredit.track_item("paper:2024")
print(ackredit.report())
```

## DueCredit interoperability

```python
from ackredit.contrib.duecredit_compat import export_to_duecredit
```

`export_to_duecredit()` forwards everything collected so far to DueCredit when it is
installed, and returns quietly when it is not. `SPEC.md` section 8 also sketches an
`export_duecredit_json()` exporter; that one is not implemented.

## Optional-dependency pattern

A host library must keep working when Ackredit is absent, so every fallback needs the
same signature as the real name — including keyword arguments such as `credit_bound`:

```python
try:
    from ackredit import scoped_usage, track_item
except ImportError:

    def scoped_usage(target, credit_bound=False):
        def deco(fn):
            return fn

        return deco

    def track_item(item_id, used_by=None):
        pass
```

The complete template, with a fallback for every exported name, lives in
[`standards/ACKREDIT_GUIDE.md`](standards/ACKREDIT_GUIDE.md) and is executed by
`tests/test_integration_guide.py`. Prefer copying it from there rather than from here.
