# Scoped MIT license audit ? 11/14/2026

**Repository:** `KingStephan18/research-portfolio`
**Baseline:** `4ec8dc7c4e494ab5042f35c0d4f443d7a0f8a28f`

## Source findings
- Baseline checkout matched public `main` and was clean.
- At baseline: 45 tracked files; no repository license.
- Existing verifier on baseline: `OVERALL: PASS`, 44 manifest entries.
- Reviewed source imports for the Python tools and their tests use the
  Python standard library; no third-party library is bundled as a dependency.
- Repository also includes acting, narrative, identity-research, website
  and independently authored research content, with separate rights and
  historical AI-assisted contribution/provenance notes.

## Scope decision
The owner expressly approved MIT for only 24 listed technical files, not
the rest of the portfolio or the separate profile repository. `LICENSE`
contains the standard MIT terms. `LICENSING.md` enumerates the exact files
and exclusions. SPDX comments identify the individual commentable files;
synthetic JSON fixtures are identified by path.

## Post-change verification and limits

- Windows 11 / Python 3.13.15: `python verify.py` returned `OVERALL: PASS`.
- Authored tests: 108 total ? 106 passed and 2 skipped because local
  Windows symlink creation was unavailable.
- The two committed JSON fixture outputs reproduced correctly.
  `permission-boundary/results.json` required an expected `guard_sha256`
  refresh after inserting its source license header; all 24 scenario
  decisions and the input fingerprint remained unchanged.
- Inventory and SHA-256 verification: 47 entries, PASS.
- Workflow textual review: `NO_RULE_MATCHES`, not a security certification.
- Explicit 24-file scope, untouched excluded works and local documentation
  links were separately checked. The profile repository was not modified.
- GitHub commit, automated CI and public license recognition must be
  verified separately after publication.

These checks do not certify copyright ownership, third-party rights,
independent security approval or acceptance into OpenAI's program.

References: `SOURCES.md`, SPDX MIT, GitHub licensing documentation, REUSE.
