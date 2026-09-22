"""ArgDigest configuration for Ackredit.

Axis 2 names one digester per argument name; axis 1 names what a function may
receive at all, which matters here for the two functions that take `**kwargs`.
"""

# Axis 2 — the value contract of each argument.
DIGESTION_SOURCE = "ackredit._private.argdigest.argument"
DIGESTION_STYLE = "package"
# The one function with open keywords is `register_item`, whose keywords are the
# fields of a work: a title is free text, a year may be "in press" (ACKREDIT-W009
# says so), a publisher is a name. There is no digester to write for most of them
# and never will be, so a warning per field would be noise on every call. Which
# *names* are admissible is axis 1's answer, and it is declared.
STRICTNESS = "ignore"
SKIP_PARAM = "skip_digestion"

# Axis 1 — the argument contract of each function.
FUNCTION_SOURCE = "ackredit._private.argdigest.function"
DOMAIN_SOURCE = "ackredit._private.argdigest.domain"
NORMALIZATION_SOURCE = "ackredit._private.argdigest.normalization"
UNKNOWN_ARGUMENT = "error"
