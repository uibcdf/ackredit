"""An installable, dependency-free producer with fictional demonstration citations."""

import asyncio

__ackredit__ = {
    "schema": "ackredit.provider@1",
    "software": {"name": "Citation Example", "version": "2.4.0"},
    "items": [
        {
            "id": "example:software:2.4.0",
            "type": "software",
            "title": "Citation Example",
            "version": "2.4.0",
            "year": 2026,
        },
        {
            "id": "example:article",
            "type": "article",
            "title": "A method for demonstration",
            "authors": ["Ruiz, Ana"],
            "year": 2025,
            "doi": "10.1234/demo",
        },
        {"id": "example:unused", "type": "article", "title": "Untaken method"},
    ],
    "functions": {
        "normalize": [
            {"item_id": "example:software:2.4.0", "roles": ["executed_software"]},
            {"item_id": "example:article", "roles": ["software_description"]},
        ],
        "unused": [{"item_id": "example:unused", "roles": ["scientific_criterion"]}],
    },
}


def normalize(values, scale=1):
    """Normalize a vector, preserving a real computation and call signature."""
    total = sum(values)
    return [value / total * scale for value in values]


def unused():
    raise AssertionError("The untaken branch must never execute")


async def async_normalize(values):
    await asyncio.sleep(0)
    return normalize(values)


# A provider's own decorator could set this attribute and return the original
# function. The function remains unwrapped and does not import Ackredit.
async_normalize.__ackredit__ = {
    "uses": [{"item_id": "example:article", "roles": ["scientific_criterion"]}]
}
