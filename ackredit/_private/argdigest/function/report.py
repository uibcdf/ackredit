"""Contract for `report`, whose extra keywords reach the renderer it resolves."""

from argdigest import FunctionContract

contract = FunctionContract(
    caller="ackredit.core.report.report",
    # A plain domain name, not ["signature", ...]: `signature` is a token that
    # only means anything as the whole value, and in a list it is read as the
    # name of a domain that does not exist. The function's own parameters are
    # admitted regardless.
    admits="format_options",
    description="Extra keywords are the options of the format's renderer.",
)
