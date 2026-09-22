"""What Ackredit costs in a real run.

Every performance claim before this came from a synthetic benchmark. Those found
two O(n squared) defects and they cannot say whether the library is light in a
real workflow, which is what roadmap theme D asks for.

The workload is MolSysMT reading a protein from the PDB and converting between
forms — a real scientific library doing real work, not a loop around
`track_item`. MolSysMT is not a dependency of Ackredit, so this is a script a
maintainer runs, not a test.

**Method.** Each measurement is the minimum of several repetitions, because
interference only ever adds time. Each runs in its own interpreter, because
imports happen once per process and because the state a previous run left would
be measured otherwise. Both modes import Ackredit, so the only difference in the
timed region is whether the feature is on — the first version of this imported
Ackredit only in the mode being measured, which made auto-discovery look faster
than no auto-discovery.

    python devtools/benchmark.py
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

REPEATS = 7

WORKFLOW = """
    import time
    import molsysmt as msm
    import ackredit

    PATH = msm.systems["T4 lysozyme L99A"]["181l.pdb"]
    MODE = {mode!r}

    if MODE != "bare":
        ackredit.register_item(
            id="molsysmt:software", type="software", title="MolSysMT",
            authors=["Prada-Gracia, Diego", "Moreno-Vargas, Liliana M."],
            doi="10.5281/zenodo.1298752",
        )
        ackredit.bind("molsysmt.convert", ["molsysmt:software"])

    if MODE == "persist":
        import tempfile
        from pathlib import Path
        ackredit.enable_persistence(Path(tempfile.mkdtemp()) / "session.json")

    def step(name, call):
        if MODE == "bare":
            return call()
        with ackredit.scope(f"molsysmt.{{name}}", credit_bound=(name == "convert")):
            ackredit.track_item("molsysmt:software")
            return call()

    start = time.perf_counter()
    molsys = step("convert", lambda: msm.convert(PATH, to_form="molsysmt.MolSys"))
    step("get", lambda: msm.get(molsys, n_atoms=True))
    step("select", lambda: msm.select(molsys, selection="atom_name=='CA'"))
    step("info", lambda: msm.info(molsys))
    step("convert", lambda: msm.convert(molsys, to_form="mdtraj.Trajectory"))
    elapsed = time.perf_counter() - start

    if MODE == "persist":
        ackredit.close_persistence()
    print(elapsed)
"""

IMPORTS = """
    import time
    import ackredit

    if {hooks!r}:
        ackredit.enable_import_hooks()

    start = time.perf_counter()
    import molsysmt  # noqa: F401
    print(time.perf_counter() - start)
"""


PER_CALL = """
    import time
    import ackredit

    ackredit.register_item(id="x:1", title="A Work")
    COUNT = 200_000

    def measure(call):
        call()                       # once, so the first-call costs are not counted
        start = time.perf_counter()
        for index in range(COUNT):
            call(index)
        return (time.perf_counter() - start) / COUNT

    if {what!r} == "track_item":
        print(measure(lambda index=0: ackredit.track_item("x:1", used_by="caller")))
    else:
        def scoped(index=0):
            with ackredit.scope("a.target"):
                ackredit.track_item("x:1")
        print(measure(scoped))
"""


def runs(source: str) -> list[float] | None:
    times = []
    for _ in range(REPEATS):
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(source)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr.strip()[-400:], file=sys.stderr)
            return None
        times.append(float(result.stdout.strip().splitlines()[-1]))
    return times


def best(source: str) -> float | None:
    times = runs(source)
    return min(times) if times else None


def line(
    label: str,
    seconds: float | None,
    against: float | None = None,
    noise: float | None = None,
) -> None:
    """Print one measurement, and say when it is smaller than the noise.

    A difference below the spread of the baseline's own repetitions is not a
    measurement of Ackredit. Saying so beats printing a number that will come
    out with the other sign on the next run — which it does.
    """
    if seconds is None:
        print(f"  {label:34} could not run")
        return
    overhead = ""
    if against:
        delta = seconds - against
        overhead = f"   {delta * 1000:+8.1f} ms   {delta / against:+7.2%}"
        if noise is not None and abs(delta) < noise:
            overhead += "   under the noise"
    print(f"  {label:34} {seconds:7.4f} s{overhead}")


def main() -> int:
    try:
        import molsysmt  # noqa: F401
    except ImportError:
        print("This needs MolSysMT, which is not a dependency of Ackredit.")
        print("  conda install -c uibcdf molsysmt")
        return 1

    print(f"Minimum of {REPEATS} runs, each in its own interpreter.\n")

    print("A workflow: read 181l.pdb, convert, query, select, convert again.")
    baseline = runs(WORKFLOW.format(mode="bare"))
    bare = min(baseline) if baseline else None
    noise = (max(baseline) - min(baseline)) if baseline else None
    line("no Ackredit", bare)
    if noise is not None:
        print(
            f"  {'its own spread over ' + str(REPEATS) + ' runs':34} {noise * 1000:7.1f} ms"
        )
    line(
        "tracked, as the guide describes",
        best(WORKFLOW.format(mode="tracked")),
        bare,
        noise,
    )
    line(
        "tracked, with persistence", best(WORKFLOW.format(mode="persist")), bare, noise
    )

    print("\nWhat one instrumented call costs, which is the number that scales.")
    for what, label in (("track_item", "track_item"), ("scope", "scope + track_item")):
        seconds = best(PER_CALL.format(what=what))
        if seconds is not None:
            print(f"  {label:34} {seconds * 1e6:7.2f} µs per call")

    print("\nImporting a library, with auto-discovery off and on.")
    baseline = runs(IMPORTS.format(hooks=False))
    plain = min(baseline) if baseline else None
    spread = (max(baseline) - min(baseline)) if baseline else None
    line("import molsysmt", plain)
    if spread is not None:
        print(
            f"  {'its own spread over ' + str(REPEATS) + ' runs':34} {spread * 1000:7.1f} ms"
        )
    line(
        "import molsysmt, hooks enabled",
        best(IMPORTS.format(hooks=True)),
        plain,
        spread,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
