"""What `report` may be told beyond the format itself.

The admissible keywords depend on the value of `format`, because they are the
renderer's own parameters — and since `uibcdf/ackredit#36` a renderer may come
from any package. So this domain is derived from the renderer table rather than
written out, which is what keeps it from drifting: `report` binds the same
signature before calling, and the two cannot disagree because both read the
renderer.
"""

from __future__ import annotations

from collections.abc import Mapping

from argdigest import Domain


class _OptionsByFormat(Mapping):
    """The options each registered format takes, read when asked.

    Not a dict: a format can be registered after this module is imported, by a
    plugin or by `register_format`, and a snapshot would not have it.
    """

    def _table(self):
        from importlib import import_module

        return import_module("ackredit.core.report")

    def __getitem__(self, format_name):
        report = self._table()
        canonical = report._ALIASES.get(format_name, format_name)
        renderer, _ = report._RENDERERS[canonical]
        return tuple(report._options(renderer))

    def __iter__(self):
        return iter(self._table()._RENDERERS)

    def __len__(self):
        return len(self._table()._RENDERERS)


domain = Domain(
    name="format_options",
    depends_on="format",
    by_value=_OptionsByFormat(),
    description="the options the renderer for that format takes",
)
