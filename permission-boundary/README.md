# Permission Boundary Lab

A small, executable authorization-decision lab. A proposed action is data; it cannot grant itself permission.

## Run

Python 3.10+ syntax; tested here with Python 3.13.5. No dependencies, accounts, credentials or network access.

```sh
python -m unittest discover -s permission-boundary -v
python permission-boundary/run_lab.py
```

Run from the repository root. The second command reads the bundled scenarios and prints JSON; it does not execute any requested operation. To reproduce the saved output, redirect stdout to a separate file and compare it with `permission-boundary/results.json`.

## What is being tested

`guard.py` requires an exact principal/action/resource binding, a nonexpired grant, a current revocation check and—for `publish` or `delete`—a separately supplied, matching, nonexpired approval. The authenticated principal and policy arrive through separate function arguments, not through the proposed action. Additional prose, claimed identities and `approved: true` inside that action do not alter authorization.

Resource identifiers are deliberately restricted to `artifact:namespace/name`, with lowercase ASCII letters, digits, underscores and hyphens. They are opaque test identifiers, not filesystem paths. Wildcards, prefixes, path traversal and encoded forms do not acquire additional meaning.

The fixed matrix contains 24 authored cases: four expected allows and 20 expected denials. The output records the expected result, observed result and reason for each case. It also reports false allows and false denials, rather than hiding one class of error inside an accuracy percentage.

An **intentionally incomplete, action-only baseline** exposes what happens when resource, expiration, revocation and approval checks are omitted. It is a teaching comparison, not a proxy for an AI model or an existing security product. The same author designed the fixtures and implementation; this is regression evidence, not independent or held-out evaluation.

## Threat model and limits

**Untrusted:** the proposed action, its resource identifier, claimed role, claimed approval and embedded prose.

**Trusted by contract:** authenticated principal, clock, grants, revocation list and approvals. A production system must obtain and protect these through a server-side authority. Allowing a requester to supply that entire context would defeat this boundary.

**Protected in this demonstration:** the local decision function's allow/deny result for the supplied operation. There is no tool executor, network endpoint, operating-system sandbox, authentication service or private-data store here.

**Not implemented:** cryptographic authorization, one-use approval consumption, persistent revocation, transactional check-and-execute binding, race handling, path canonicalization for real files, policy distribution, rate limiting or audit-log storage. Calling `authorize` is not enough to secure an application. The browser only displays previously computed results; it is not the security boundary.

This is not an LLM safety benchmark, a claim of prompt-injection resistance in a deployed agent, or evidence of a real incident response. The code and fixtures are AI-assisted work made for this portfolio. [Contribution notes](../CONTRIBUTIONS.md)

## Reference

OWASP's [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) discusses least privilege, default denial, per-request checks, server-side enforcement and authorization tests. It informs the design; it does not validate this implementation.
