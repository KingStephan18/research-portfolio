# Current repository validation — 10/24/2026

[Detailed public audit and fixes](security-research/AUDIT_2026-10-24.md).

The current `python verify.py` run on Python 3.13.5 / Linux passes **108 tests**: 45 Evidence Ledger, 23 Permission Boundary Lab, 25 Maintainer Workflow Review and 15 repository-audit checks. Both committed JSON results are reproduced exactly. The verifier checks manifest syntax, uniqueness, canonical relative paths, complete non-ignored artifact coverage and content hashes; an empty or incomplete manifest no longer yields PASS. Git internals, bytecode, `.venv`, `.env`/`.env.*` and the OS metadata files listed in `.gitignore` are excluded from inventory; they cannot be added as manifest artifacts. Store local audit logs outside this snapshot or they will correctly appear as unlisted files.

Tests added in this audit first reproduced the relevant failure modes and then passed after repair. All 16 embedded downloads and three inline scripts in `index.html` were compared with the previous public version and remain unchanged. The two embedded ZIPs retain valid CRCs, safe member paths and matching internal manifests.

Chromium rendered the staged HTML at 1440×1000, 768×1024 and 390×844, with no horizontal overflow or JavaScript errors; the existing filters and JavaScript-disabled content were checked. These checks used the document contents in an isolated browser: file/localhost URL navigation was blocked by that environment, so this is **not** an anonymous live-site or network-navigation test. CSP script hashes and internal fragments passed separate static checks.

The tests run only local synthetic fixtures; they are not scans of the owner's computer or third-party infrastructure. No Windows execution, other Python-version execution, independent security certification or complete secret-detection claim is made. Source-only analysis and recorded upstream advisories do not validate original vulnerability candidates.

---

## Historical validation record (retained)

# Validation

Edition 4.2 · 09/26/2026

## Reproducible technical checks

Run `PYTHONDONTWRITEBYTECODE=1 python verify.py` from the repository root. The environment variable prevents test-run cache files from entering release bundles; it is not a security control. On Windows, use the equivalent environment-variable syntax for your shell.

The source targets Python 3.10+ syntax. Python 3.13.5 was exercised in the build environment. The suite consists of 45 Evidence Ledger tests and 23 Permission Boundary Lab tests. The verifier also regenerates both result files and checks the committed SHA-256 manifest.

## Publication checks

The release audit traverses the source bundle and every base64 download embedded in the HTML, including nested ZIP archives. It checks archive paths, duplicate entries, cache files, image assets, PDF image objects and selected private-data patterns. Individual downloads are compared with their source bytes, and each archive manifest is verified against its own contents.

The page is checked in Chromium at desktop, tablet and phone widths, with and without JavaScript. These local checks do not establish the status of a hosted site; the actual emitted site and repository must be inspected after staging and any authorized publication.

The public page uses typography rather than photographs. No portrait, headshot or recorded acting reel is supplied.

## Limits

Tests are authored regression checks, not held-out evaluation or independent certification. Selected privacy scans are not exhaustive secret detection. Browser checks are not an accessibility certification. The unproduced screen work is not a film credit, audition or professional casting assessment.

## Additive maintainer-security check — 10/21/2026

A separate author-created `maintainer-security` module was added without replacing the original edition 4.2 fixtures. Its **20 deterministic synthetic tests** completed on Python 3.13.5 in the working environment, including review signals for mutable Actions/container references, privileged triggers, PR-derived fields, overly broad tokens, and bounds/error behavior. `python -m unittest discover -s maintainer-security -v` is the reproduction command. The repository's `verify.py` now includes this third suite. The earlier 45 Evidence Ledger and 23 Permission Boundary Lab tests were verified for edition 4.2 but were **not independently re-executed in this extension's temporary working directory**. Do not infer an independent security audit, actual CI execution or validation on other Python versions.

`workflow_review.py` uses deliberately limited text heuristics, not complete YAML parsing or GitHub runtime semantics. A `NO_RULE_MATCHES` result does not mean a workflow is safe; `NOT_ASSESSED` is returned for absent/unreadable workflow inputs. This addition is **not incorporated into embedded HTML downloads**, which remain edition 4.2; published source files and the updated integrity listing are authoritative for the extension. No license was assigned and no GitHub Release was created in this operation.
