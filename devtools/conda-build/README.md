# Conda packaging

Ackredit builds one `noarch: python` artifact. Dependencies such as NumPy carry
their own platform packages. Published 0.9.0 was qualified on Linux x86-64 and
macOS arm64 on Python 3.11–3.14. Its exact public identity and qualification
receipts are retained in [the delivery record](../../devguide/archive/ackredit_cannot_be_installed.md).

## Committed candidate inputs

`release_plan.toml` records staging, version/build, executed source gates and
the installed matrix. `resources.toml` names packaged code, generated version,
`CITATION.cff`, the launcher and full installed suite. Runtime receipts bind
the final full source SHA and actual artifact digest; a commit cannot contain
its own SHA. Changed inputs invalidate the gates that consumed them.

The wrappers pin shared MolSysSuite operations independently: build/upload at
`2fb344525ca0eea817dc24a518f4a6bf26e311cf`, installed qualification and promotion
at `c3e2b9b3dabf3d1c65349c389a23048957bea21a`, and publication policy at
`2a2a459cc3795bb92766fffa0fe28f4d80f01ad4`. The provider owns
archive inspection, executed-gate acquisition, exact-file upload, label-only
promotion and independent public registry/index verification.

## Staging and qualification

1. Publish the reviewed source commit and pass its declared CI/policy gates.
2. Dispatch `build_and_upload_conda_packages.yaml` with full `candidate_sha`
   and the version in the plan (currently `0.10.0`). The plan supplies build 0. The provider freezes version
   metadata only in its ephemeral checkout, builds once, tests and inspects the
   archive before uploading the exact file to staging.
3. Retain its producer artifact/receipt. Dispatch `test_staged_conda_package.yaml`
   with the original producer `candidate_sha`, exact filename and SHA-256.
   Select the reviewed qualification ref; its native `qualification_sha` is
   recorded separately if the caller was corrected after production. The
   source-binding receipt preserves both identities without rebuilding the file.
   All eight cells must install that file, verify Conda provenance, resources and
   launcher, and execute the complete suite outside source. Dependencies resolve
   through public channels; staging supplies only the Ackredit candidate.
4. Record receiving-consumer compatibility separately. Development source/wheel
   evidence does not establish the first public consumer dependency closure.
   For 0.10.0, dispatch `function_provider_receiving.yaml` with the original
   `candidate_sha`, `conda_version`, `conda_filename` and `conda_sha256`. Its Conda
   profile builds only the pinned real producer and original 0.9.0 fallback as
   wheels. Shared operations install and verify the exact candidate before and
   after science; all eight cells execute six mandatory real receiving tests.
   Require its successful aggregate before public promotion in addition to the
   full installed matrix. This scientific gate does not replace the installed
   matrix consumed by the shared promotion verifier.

## Public promotion

After the release decision, dispatch `promote_conda_package.yaml` with source
SHA, version, staged SHA-256 and the successful installed run ID. Supply
`qualification_sha` when the installed caller differs from the producer source.
The provider
queries native matrix/step evidence, adds `main` to the same file and verifies
its public label and solver index. It never rebuilds or overwrites that coordinate.
Recheck a failed read-only post-public verifier without repeating promotion.

The old combined `promote: true` interface is replaced: it rebuilt and reuploaded
instead of promoting tested bytes. Repairs use additive builds with new installed
evidence. Public tags are immutable; staging creates no remote release tag.

After verified promotion, register the canonical version tag at the original
producer source recorded in the delivery receipt, even when a later caller
qualified the unchanged archive. Reinstall editable development distributions
after updating tag history so their metadata derives from the published release
baseline and satisfies consumer minima. Ackredit #82 records the 0.9.0 correction;
`tests/test_versioning.py` checks installed identity against public receipts.
GitHub Release/DOI publication retains its own recorded outcome.

`ANACONDA_UIBCDF_TOKEN` is mapped explicitly to the shared secret. Secret
availability, upload permission and verified public delivery remain separate.
No installation command or badge claims publication before verification.

The authority is `MOLSYSSUITE_GUIDE.md`, routing to central release/distribution/
Conda policies. Ackredit #22 owns this route; #75 owns the portable contract and
#80 owns Python 3.14 delivery and receiving-consumer closure.
