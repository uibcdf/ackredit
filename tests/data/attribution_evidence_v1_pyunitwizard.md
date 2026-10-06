# Original hosted recorder-evidence fixture

`attribution_evidence_v1_pyunitwizard.json` is the unmodified complete companion
from `receiving-ubuntu-latest-py3.13` in Ackredit #106's
[installed receiving run](https://github.com/uibcdf/ackredit/actions/runs/37421954520).
It is original development evidence, not a newly produced 0.11.0 artifact or an
independent scientific validation.

Native artifact ID: `11393945286`; original ZIP SHA-256:
`509b3f084e7861996d3a3d186a978085a6a312077d377a569404a4446ed243cb`.
The original JSON SHA-256 is
`25c2807ba903d3136d8a4469012837a9b3b74bd9d09b9702e9ab27641fee7b67`.
Both were rechecked against the maintained
[original receipt](https://github.com/uibcdf/ackredit/blob/42d30e4e081601ec1198331f0fb3e23b6b12f12b/devtools/receipts/workflow_recorder_evidence_hosted_106_2026-10-06.json)
when retained under #114 on 2026-10-06.

Producer source `9ca7157323d816925da99560dc4ef68b604396ed` supplied Ackredit
`0.10.1+20.g9ca7157`; pinned PyUnitWizard source was
`0e422d06b0af56e4dd2b43cafd00f059221eb405`. Four original occurrences retain a
real Pint conversion, a reused Pint-to-unyt conversion, a controlled recording
fault, and selected-but-unused observation. The diagnosed fault was deliberately
introduced by qualification; it is not a failure of that scientific conversion.
Other backend recorder origins stay unknown. Recorder identities remain those
of the original producer, independent of the reading installation.

`tests/test_attribution_evidence.py` checks these original bytes and their saved
default/integrated reports, including a fresh producer-blocked offline CLI
reader that refuses new credit and emits no stored diagnostics. The historical
report hashes guard current behavior; they do not independently decide whether
all future cosmetic report changes are incompatible.
