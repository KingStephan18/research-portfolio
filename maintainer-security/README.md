# Maintainer Workflow Review — offline supply-chain checks

**Published 10/21/2026; input-handling revision 0.1.1 on 10/24/2026.** A small, inspectable, read-only Python reference tool for maintainers reviewing selected GitHub Actions risks. Software supply-chain compromise is a cross-border concern: a single upstream workflow can expose credentials, alter releases, or affect downstream users. This tool only identifies a limited set of patterns **for human review**; it cannot establish that any repository is secure or compromised.

## Run

Python 3.10+; standard library only. No GitHub token, installation, API access, network, shell execution of workflows, or account modification.

```sh
python -m unittest discover -s maintainer-security -v
python maintainer-security/workflow_review.py /path/to/your/repository
```

The scanner reads direct `.yml` / `.yaml` files in the specified repository's `.github/workflows/` directory. It prints deterministic JSON containing **review metadata: rule IDs, relative filenames, line numbers, counts and status/error codes**, never the workflow's contents, secrets or environment values. It never modifies the target. Exit codes: `0` = no rule matches (not a security pass), `1` = review findings, `2` = no workflows or unassessable input. Tests create synthetic temporary workflows; no real workflows are run.

## Rules (review signals, not vulnerability verdicts)

| Rule | Meaning |
| --- | --- |
| `UNPINNED_ACTION` | A `uses:` reference is not pinned to a full 40-digit Git commit SHA. |
| `DYNAMIC_ACTION_REFERENCE` | The action reference is dynamic; manual resolution is needed. |
| `MUTABLE_CONTAINER_REFERENCE` | `docker://` is not pinned to a full SHA-256 digest. |
| `PRIVILEGED_TRIGGER_REVIEW` | `pull_request_target` or `workflow_run` event appears in an event-like position. |
| `UNTRUSTED_EXPRESSION_REVIEW` | Selected issue/comment/PR title or body expressions warrant inspection for unsafe interpolation. |
| `UNTRUSTED_CHECKOUT_REF_REVIEW` | PR-head-derived checkout ref appears. |
| `UNSAFE_PR_CHECKOUT_OPT_IN` | GitHub's explicit unsafe PR checkout option appears. |
| `BROAD_WRITE_ALL` | Explicit `permissions: write-all` appears. |
| `NO_EXPLICIT_PERMISSIONS_FOUND` | No conventional `permissions:` key was found by the textual check. |

The code uses deliberately conservative **textual heuristics**, not a YAML parser or a semantic Actions analyzer. It can miss threats or flag harmless constructs. YAML aliases, inline/multiline structures, event scoping, inherited token permissions, expression flow, remote action trust, image provenance and complex shell quoting require independent inspection. Pinning a SHA limits mutable-tag risk; it does **not** prove the pinned code is trustworthy. Local actions (`./...`) are excluded from remote pin checks but still need code review. `NO_RULE_MATCHES` never means `SAFE`.

A missing workflow directory is `NOT_ASSESSED`, not evidence of a vulnerability. The portfolio itself currently documents executable **Python samples** and does not establish that GitHub Actions CI exists. This scanner can audit **another repository supplied locally**; it is not turned on against any third-party project automatically.

## Threat model, verification and appropriate tools

Inputs are untrusted workflow **text**. Trusted assumption: the operator selects the root on a machine they control. The script rejects observed symlinks at the supplied root, `.github`, `workflows` and workflow-file levels, files above 256 KiB, invalid UTF-8, more than 100 workflow files, and directories exceeding 1,000 entries. Directory enumeration is streamed; the actual file read is bounded to 256 KiB plus one byte to detect growth. Filesystem errors return `NOT_ASSESSED` with exit code 2 instead of exposing exception text. These checks are not an atomic filesystem sandbox: use a stable, operator-controlled local tree, not one concurrently modified by an adversary. It neither downloads dependencies nor authenticates repositories, so it cannot verify origin, commits, packages, signatures, runtime behaviors or any CVE. Do not run it as a privileged web service or use results as a release authorization decision.

Prefer GitHub's own security settings and CodeQL, OpenSSF Scorecard, dependency review, secret scanning, manual threat modeling, independent security review and tested incident-response procedures for production use. These tools complement, rather than validate, this prototype.

Research and practical controls: [global threat model](THREAT_MODEL.md), [original Permission Boundary Lab](../permission-boundary/README.md), [references](../SOURCES.md), [test evidence](../VALIDATION.md). No outside sponsor, formal certification, customer adoption or independent evaluation is claimed.

## 10/24/2026 regression audit

Five added tests cover denied directory access, failing metadata reads, a file growing after its size check, workflow-count limits and total directory-entry limits. The complete module suite now has **25 passing tests** in the recorded Python 3.13.5 Linux run. The original fixture describing read-only permissions was also corrected to valid block-style YAML. See [the public audit](../security-research/AUDIT_2026-10-24.md) for scope and remaining limitations.
