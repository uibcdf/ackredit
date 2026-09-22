---
summary: Ackredit fetched as fast as it could, identified no contact, and reported a rate-limited response as a network problem.
issue: uibcdf/ackredit#48
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: measured
area: [core, discovery]
guard: tests/test_api_politeness.py
normative: docs/content/user_guide/registration.md
blocked_by: []
supersedes: []
---

# Not a polite client

## What

Ackredit fetches metadata from Crossref and DataCite on behalf of whoever installs it, so
it is a client running on many machines at once.

**It ignored the rate limit those services advertise.** Crossref returns it on every
response, and says which pool the request landed in:

```
Ackredit/0.6.0 (https://github.com/uibcdf/ackredit)
  x-api-pool: public-single   x-rate-limit-limit: 5   x-rate-limit-interval: 1s
```

`enrich_all` issued one request per item with nothing between them. Measured against a
stand-in that answers instantly, 60 requests left in 11 ms — 5 326 per second against an
advertised 5. On a real network the latency is what limited it, which is not a policy.

**It was in the public pool because it identified no contact.** The same request carrying a
`mailto:` comes back `x-api-pool: polite-single`, `x-rate-limit-limit: 10`.

**A rate-limited response was reported as a network problem.** An HTTP 429 was caught with
everything else and became `ACKREDIT-W006`, whose user message says to check network
access.

## How

`_fetch` waits so the advertised rate is respected, adopts the limit and interval the
service states in place of what was assumed, and on a 429 waits the advertised interval and
tries once more before letting the error through.

A contact reaches the `User-Agent` when the user sets `ACKREDIT_CONTACT_EMAIL`, and only
then. Until a response says otherwise the throttle assumes the public pool's five per
second, which is what an unidentified client is allowed.

## Why

The measurements come from the services themselves rather than from documentation: the
headers say which pool a request landed in and what it is allowed. A library that asks
faster than it is allowed, from every machine that installs it, is the kind of client rate
limits exist for.

## What was refuted

- **Baking in a maintainer's address to take the polite pool.** It would attribute every
  user's requests to one person and misuse the allowance that identification earns. A
  guard asserts no address is in the source.
- **Sending a contact by default from some other source**, such as git config. Sending an
  address to a third party is the user's decision, and a default is not one.
- **Assuming the polite pool's ten per second.** It is the rate for a client that has
  identified itself, and Ackredit has not until the user says so.
- **Retrying a 429 more than once, or backing off exponentially.** Enrichment is optional
  and its failure is already reported; one retry at the interval the service named covers
  a shared address briefly exhausting the quota, and more turns a convenience into a
  program that will not give up.

## Scope and exclusions

Covers how requests are made. How long a cached answer stays good is still open, and is
what keeps `enrich_all` provisional.

## Acceptance criteria

- no contact is sent unless one is set, and none is in the source — met;
- requests are spaced by the advertised rate, and no window holds more than it allows —
  met, measured with a stand-in so the guard needs no network;
- the rate a service states is adopted, and a header that makes no sense leaves it
  alone — met;
- a 429 is tried once more and then reported, and another error is not retried — met;
- `tests/test_api_politeness.py` guards it: 2 of its 15 tests fail without the throttle,
  2 without the retry, and 4 with an address baked in.

## Also fixed here

The window guard as first written asked for twenty requests against a limit of fifty, so it
could not fail. It asks for more than the window allows now. A guard that cannot fail is
the defect `tests/test_workflow_hygiene.py` exists for, written by hand into a new file.
