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
