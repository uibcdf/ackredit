(User_ExampleLibraries)=
# Two libraries, one report

Everything so far described Ackredit. This page runs it.

The repository carries two small host libraries under `examples/`. They compute nothing
interesting; they are integrated exactly the way a real library would be, and the test
suite asserts they behave. **DummySolver** solves a dummy system. **DummyPipeline** calls
DummySolver, so citations cross a library boundary and the provenance has something real
to describe.

## What each one declares

A host says what it *could* cite while it is being imported. That is the moment it has,
and the registry is shared, so it outlives any run:

```python
register_item(
    id="dummysolver:2026:method",
    type="article",
    title="A direct method for dummy systems",
    authors=["Ruiz, Ana", "Gómez, Luis"],
    year=2026,
    doi="10.1234/dummy.2026.001",
)

bind(target="dummy_solver.solve", items=["dummysolver:2026:method"])
```

The method paper is bound, because every path through `solve` rests on it. The iterative
paper is not: only the branch that refines credits it.

```python
@scoped_usage(target="dummy_solver.solve", credit_bound=True)
def solve(system, method="direct"):
    if method == "iterative":
        track_item("dummysolver:2026:iterative")
        return f"{system} solved iteratively"

    return f"{system} solved directly"
```

## The same code, two bibliographies

```python
import ackredit
import dummy_pipeline

dummy_pipeline.analyse("system A")
sorted(ackredit.get_used_items())
```

```
['dummypipeline:2026:workflow', 'dummysolver:2026:method']
```

```python
dummy_pipeline.analyse("system A", method="iterative", use_reference=True)
sorted(ackredit.get_used_items())
```

```
['dummypipeline:2026:workflow',
 'dummypipeline:dataset',
 'dummysolver:2026:iterative',
 'dummysolver:2026:method']
```

Four citations instead of two, from the same call to the same function. The refinement
paper and the reference dataset appear only in the run that reached them. That difference
is the whole argument: a citation list built from what a library *contains* cannot make
it.

## Where a citation came from

```python
ackredit.report(format="provenance")
```

```
# Citation Provenance Graph

└── dummy_pipeline.analyse
    ├── (Cite: A workflow for dummy analyses)
    └── dummy_solver.solve
        └── (Cite: A direct method for dummy systems)
```

Neither library knows what the other cites. DummyPipeline never mentions the solver's
papers, and the tree still shows which call brought them in.

## Running them yourself

```bash
git clone https://github.com/uibcdf/ackredit.git
cd ackredit
PYTHONPATH=examples python -c "
import ackredit, dummy_pipeline
dummy_pipeline.analyse('system A', method='iterative')
print(ackredit.report())
"
```

## What they are for

They are documentation and test fixtures, and they are not part of the installed package.

They are also not a substitute for a real integration. A host library written here makes
the mistakes we anticipated; the value of an outside library adopting Ackredit is that it
will make one we did not. These lower the cost of that, and the roadmap keeps the two
apart.
