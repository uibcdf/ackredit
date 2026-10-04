(Dev_Interoperability)=
# Interoperability

`export_to_duecredit()` forwards references observed in the current Ackredit
session to DueCredit, when that optional dependency is installed. An item with a
DOI is forwarded as a DOI entry; other records use Ackredit's BibTeX renderer.
The call returns nothing. A failed individual export emits `ACKREDIT-W013` and
does not discard other references. Missing DueCredit is handled by the declared
optional dependency guard. The bridge does not import DueCredit observations.

Portable result attribution is a separate interoperability boundary. Clients
save `Attribution.to_dict()` or `to_json()` beside their scientific results and
read it through the corresponding `Attribution` constructors. A fresh reader
renders the saved bibliography without the original scientific engines or new
execution credit. See the [portable attribution contract](../user_guide/portable_attribution.md).
