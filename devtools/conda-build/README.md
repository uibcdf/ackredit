# Conda packaging

Ackredit is pure Python, so `meta.yaml` builds one `noarch` package that installs on
Linux, macOS and Windows across the supported interpreters. There is no build matrix.

## The release route, and why it has two steps

A published package cannot be withdrawn the way a commit can be amended, and
`devguide/release_version_policy.md` forbids moving or deleting a published tag. So a
candidate is verified before it is public, not after:

1. **Stage.** `build_and_upload_conda_packages.yaml`, run from the Actions tab, builds
   the candidate and uploads it to `uibcdf/label/staging`. The three inputs —
   `candidate_sha`, `version`, `build_number` — must describe one immutable thing, and
   the workflow refuses if they do not agree with each other or with the tag.
2. **Verify.** The same run then creates a fresh environment, installs the candidate
   *from the staging label*, and checks that it reports the expected version, discovers
   its own `CITATION.cff`, renders a report and exposes its command line.
3. **Promote.** Only with `promote: true` does the artifact reach the public label.

Run it once with `promote: false`, read the verification step, and run it again with
`promote: true` when satisfied. `build_number` is incremented only to supersede a
defective staged artifact; a released one is never replaced.

## What the recipe tests

The `test:` block runs against the built package rather than the source tree, which is
where two defects have already hidden:

- `uibcdf/ackredit#2` — the wheel shipped only `__init__.py` and `cli.py`, and an
  editable install hid it;
- `uibcdf/ackredit#21` — `CITATION.cff` lived at the repository root, which is the
  package's parent under an editable install, so discovery worked from a checkout and
  the built artifact carried nothing.

Both now fail the recipe's own tests if they return.

## Locally

```bash
GIT_DESCRIBE_TAG=$(git describe --tags --abbrev=0) \
  conda build devtools/conda-build --no-anaconda-upload -c uibcdf -c conda-forge
```

`GIT_DESCRIBE_TAG` is set by conda-build in a normal invocation; it is passed explicitly
here because `conda render` and a direct build from a worktree may not derive it.
