# Evidence Ledger
## When several references still mean one source

**Type:** AI-assisted technical demonstration. **Data:** entirely synthetic. **Built:** 09/26/2026.

### The question

Can a small, inspectable tool surface mistakes in how a research note links its claims to evidence, without pretending to automate judgment?

### The artifact

[ledger.py](../evidence-ledger/ledger.py) reads a JSON source registry and a set of claims. It checks reference integrity, collapses declared common-origin support, marks documentary contradictions and excludes reconstructions from documentary support.

The supplied packet contains seven invented sources and five claims. The first example has two references that both come from the same job event. Another example distinguishes a control's configuration record from a later access event. A third attaches only an illustrative reconstruction. These cases model how plausible reporting can overstate its own evidence.

### What ran

This revision ran 45 unit and command-line tests under Python 3.13.5, including 14 new regression tests. The tested behaviors include shared origin, independent origins, conflicting relations, context-only evidence, reconstruction, invalid schemas, duplicate records, unknown references, malformed JSON and missing input files. The bundled [results.json](../evidence-ledger/results.json) was generated from the supplied dataset.

### What the result means

`TRACEABLE` means the claim has documentary evidence labeled as supporting it, with no declared contradiction and no structural flag. Shared origins and reconstructions now produce `REVIEW_REQUIRED` rather than a clean traceability status. It does not mean the source is authentic, the wording is entailed, or the claim is true. The `truth_verdict` field therefore remains null.

The deliberately compound first claim illustrates the boundary. The checker flags that two references share an origin and requests review; it cannot itself decide which clause to rewrite. A researcher must narrow the claim.

### Design choices

The sample has no model calls, external dependencies or hidden grading rules. Its input and output can be inspected in a text editor. It rejects ambiguous duplicate evidence links rather than silently guessing how to combine them. It reports validation errors without echoing the input packet.

### Next useful extension

A separate, explicitly evaluated semantic review layer could test whether excerpts support each atomic claim. That layer is not implemented or benchmarked in this edition. A meaningful next experiment would use held-out, human-labeled claims and report false positives as well as failures to find support.

[Run instructions and limitations](../evidence-ledger/README.md) · [Contribution notes](../CONTRIBUTIONS.md)

### Audit-driven hardening

New failing tests identified duplicate JSON keys being silently overwritten, acceptance of non-finite numeric values, an uncaught Unicode output error and warning cases still appearing as clean `TRACEABLE` results. Strict decoding, bounded input reads, Unicode validation and review-state changes address those reproduced cases. These are fixes to this demonstration, not vulnerability findings in an external system.
