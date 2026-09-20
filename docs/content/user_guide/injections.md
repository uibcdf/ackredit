# Injections

FlowCite can also register items for external libraries that are not FlowCite-aware. Use:

```python
from flowcite import add_injection

add_injection("mdtraj", ["external:mdtraj:paper"])
```
