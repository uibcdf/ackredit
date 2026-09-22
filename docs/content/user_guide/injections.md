(User_Injections)=
# Injections

Ackredit can also credit external libraries that are not Ackredit-aware. An injection
says: a process that imports this module cites these items.

```python
import ackredit

ackredit.add_injection("mdtraj", ["external:mdtraj:paper"])
ackredit.enable_import_hooks()
```

Injections are credited by the import hooks, so nothing is credited until
`enable_import_hooks()` has been called. After that, the order does not matter: an
injection is credited when its module is imported, and immediately if the module was
already imported — before the hooks were enabled, or before the injection was declared.
That is what makes an injection the way to credit a package such as numpy, which
automatic discovery cannot see once it is loaded (see
[Automatic Discovery](User_Tracking)).

An injection on a standard-library module is honoured, although discovery skips the
standard library.
