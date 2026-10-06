# Citation provider example

This independently installable package uses only Python's standard library.
Its `__ackredit__` declaration and function metadata require no Ackredit import,
decorator or runtime dependency. References, names and DOI are fictional; replace
them with your own verified bibliography before using this as a template.

From an Ackredit repository checkout, install the producer in a fresh environment:

```bash
python -m venv /tmp/citation-provider-env
/tmp/citation-provider-env/bin/python -m pip install ./examples/citation_provider
/tmp/citation-provider-env/bin/python -c 'import citation_provider; print(citation_provider.normalize([1, 3]))'
```

The result is `[0.25, 0.75]` without installing Ackredit. On Windows use the
environment's `Scripts/python.exe` instead of `bin/python`. Building uses
setuptools; the installed package has no runtime requirements.

The module demonstrates software and article references for `normalize`, a
declared `unused` branch that earns no credit unless called, and function-only
metadata on `async_normalize`. The last example records its declared article
when awaited under observation; its internal call to `normalize` separately
records the software and description references.

For client-owned observation with public Ackredit >=0.11.0, install Ackredit
separately through its documented Conda route and install this producer into
that environment. Then run:

```python
import ackredit
import citation_provider

with ackredit.observe_calls(citation_provider), ackredit.capture("example") as run:
    assert citation_provider.normalize([1, 3]) == [0.25, 0.75]
print(run.attribution.report(format="bibtex"))
```

Development Ackredit after 0.11.0 additionally provides provisional
`ackredit.validate_provider(citation_provider)`. That offline validation records
no credit and installs no observation wrappers. Public 0.11.0 validates at
observer activation and does not include the standalone validator.

See the [concise author guide](../../docs/content/user_guide/provider_authors.md)
and [full protocol](../../docs/content/user_guide/function_providers.md).
The maintained installed-package guard is
`tests/test_function_providers.py::test_normally_installed_provider_and_reader_outside_checkout`.
