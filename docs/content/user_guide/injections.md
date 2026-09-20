(User_Injections)=
# Injections

Ackredit can also register items for external libraries that are not Ackredit-aware. Use:

```python
from ackredit import add_injection

add_injection("mdtraj", ["external:mdtraj:paper"])
```
