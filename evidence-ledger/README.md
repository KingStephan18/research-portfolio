# Evidence Ledger

A small deterministic Python example for reviewing **reference structure**, not deciding truth.

## Scope

The input contains a source registry and claims with manually assigned evidence relations. Sources can be primary, secondary or reconstruction. The author also supplies origin groups. Repeated supporting references in one origin group are counted once.

Output review states:

- `TRACEABLE`: documentary support is declared, no contradiction is declared, and there are no structural flags. This is still not a truth verdict.
- `CONFLICT`: documentary support and contradiction are both declared. Human review is required.
- `REVIEW_REQUIRED`: contradiction without documentary support, or any shared-origin/reconstruction flag without a documentary conflict. Supporting-origin counts remain visible; warning states are not presented as clean passes.
- `UNSOURCED`: no documentary support, contradiction or reconstruction is linked. Context-only references do not establish support.

`SHARED_ORIGIN` flags repeated supporting origins. `RECONSTRUCTION` flags an illustrative source; it contributes neither documentary support nor documentary contradiction. A source cannot occur twice within one claim; split ambiguous statements rather than encoding opposing relations against the same source.

## Use

Requires Python 3.10 or later; standard library only.

```sh
python -m unittest -v
python ledger.py claims.json
```

The CLI prints JSON to standard output. To retain a fresh result deliberately:

```sh
python ledger.py claims.json > my-results.json
```

Malformed input produces exit status 2 without printing the supplied data. This demonstration accepts only inputs explicitly marked `synthetic: true`, with a 2 MB CLI input limit. Duplicate JSON object keys, non-finite numbers, numeric overflow and invalid Unicode scalars are rejected. The size limit bounds the actual file read. It makes no network request and performs no model inference. Inputs are local files; this CLI is not an upload service or an operating-system sandbox.

## Contents and limits

`claims.json` contains **7 sources and 5 claims**, all invented for this portfolio. `results.json` is the generated checker output. The **45 unit/CLI tests** ran successfully in this revision under Python 3.13.5. Compatibility below that version follows the code's Python 3.10 syntax target; those interpreters were not executed.

Important failure modes remain outside this checker: a fabricated but well-formed citation; an inaccurate source excerpt; false `supports` labels; wrong origin-group assignments; omitted contradictory evidence; ambiguity inside a compound claim; and a malicious actor deliberately labeling real private data synthetic. Schema acceptance does not validate those things. The synthetic flag is a declared boundary, not an enforced privacy classifier.

C01 deliberately contains a compound statement about completion and independent confirmation. The program flags shared origin, but a person must split and correct the wording. Do not report this result as automated semantic verification.

This is a reference implementation and teaching sample, not a production security product or a benchmark of an AI model. Authorship is documented in [CONTRIBUTIONS.md](../CONTRIBUTIONS.md).

## Revision note

The original 28-test suite passed before this audit. The first fourteen regression tests exposed eight failures across warning presentation and parser/error handling. Three additional tests exposed Unicode gaps in ignored metadata, nested arrays and object keys. The revised suite passes all 45 tests. The original reconstruction-with-support expectation changed deliberately to `REVIEW_REQUIRED`; reconstruction still does not count as documentary contradiction. See [validation notes](../VALIDATION.md).
