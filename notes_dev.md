## Behavior expected

```python
import ackredit

ackredit.register_item(...)
ackredit.bind(...)
ackredit.scoped_usage(...)
print(ackredit.report())
```

compatibility

```python
from ackredit.contrib.duecredit_compat import (
    export_duecredit_json,
    inject_into_duecredit,
)
```

in a third-party library should work as intended:

```python
try:
    from ackredit import scoped_usage, track_item
except ImportError:

    def scoped_usage(target=None):
        def deco(fn):
            return fn

        return deco

    def track_item(*args, **kwargs):
        pass
```

## How to use it

```python
try:
    from ackredit import scoped_usage, track_item
except ImportError:
    # graceful fallbacks
    def scoped_usage(target=None):
        def deco(fn):
            return fn

        return deco

    def track_item(*args, **kwargs):
        pass
```

