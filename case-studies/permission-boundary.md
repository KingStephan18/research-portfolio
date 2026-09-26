# Permission Boundary Lab
## A proposed action is not permission to take it

**Artifact:** executable Python decision logic, 24 synthetic scenarios, 23 unit/CLI tests and generated results. **Status:** local demonstration; no real account, repository or AI model was tested.

### Question

What happens when an assistant proposes an action outside its current authority, or includes text that claims the action has already been approved?

### Design

Separate the requested action from the authority used to judge it. The lab accepts the principal, grants, time, revocations and approvals as trusted caller context. A request may propose `read`, `write`, `publish` or `delete` against one opaque resource. It may not supply its own identity, extend a grant through prose or turn a self-declared approval into a trusted one.

The policy uses exact matches rather than path prefixes. An expired or revoked grant does not remain effective because it once permitted the operation. A high-impact operation needs both a live grant and a fresh approval bound to the same principal, action and resource.

### Experiment

The supplied matrix contains: four legitimate operations and 20 denial cases, including wrong resources, changed actions, expiration boundaries, revocation, forged approval fields and malformed requests. The runner compares observed decisions and reason codes against those explicit expectations. An intentionally incomplete baseline checks only principal and action.

The local run produced **0 false allows and 0 false denials for the guarded function** on these 24 fixtures. The intentionally incomplete baseline produced **12 false allows and 0 false denials**. These counts describe this authored matrix only. They are not estimates of real-world failure rates or comparisons with commercial systems.

[Inspect every result](../permission-boundary/results.json) · [Inspect the scenarios](../permission-boundary/scenarios.json) · [Read the implementation](../permission-boundary/guard.py)

### What this demonstrates

The artifact makes a security requirement executable and shows a concrete failure when checks are removed. It gives a reviewer a decision function, positive controls, negative controls, a threat model and reproduction commands—not only a statement that privacy matters.

### Remaining boundary

The context must actually come from trusted infrastructure. The demonstration does not authenticate users, execute operations, consume one-use approvals or close check-to-execution races. A real integration needs those mechanisms and independent testing. No model was called, and the fixtures are not held out.

[Run and threat model](../permission-boundary/README.md) · [Contribution notes](../CONTRIBUTIONS.md)
