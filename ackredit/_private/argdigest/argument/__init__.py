"""One digester per argument name, found by module name.

A digester is `digest_<argument>` in `<argument>.py`, and it runs for every
decorated function that takes an argument of that name. Which functions those
are is deliberate and measured — see `ackredit/_private/argdigest/digest.py`.
"""
