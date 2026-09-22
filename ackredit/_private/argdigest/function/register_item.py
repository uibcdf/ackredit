"""Contract for `register_item`, whose keywords are the fields of a citation."""

from argdigest import FunctionContract

contract = FunctionContract(
    caller="ackredit.core.registry.register_item",
    admits="citation_field",
    description="Keywords are the fields of the work being declared.",
)
