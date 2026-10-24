# Live repository maintenance — 10/24/2026

- Added current cybersecurity research to the existing website navigation and page; corrected its stale footer edition label. The 16 embedded edition 4.2 downloads are unchanged.
- Maintainer Workflow Review 0.1.1 now handles metadata/enumeration failures without a traceback, bounds the actual file read and streams directory entries with explicit limits; five regression tests were added.
- The repository verifier now rejects empty, malformed, duplicate, incomplete or unsafe manifests, checks complete non-ignored artifact coverage, and reports subprocess failures cleanly.
- Added 15 repository-audit tests and reran the full suite: 108 tests pass in the documented environment. Updated sources, validation and the public research log.
- No license, repository permissions, private data stores, archived download contents or original teaching datasets were changed. See [audit evidence](security-research/AUDIT_2026-10-24.md).

## Historical edition notes

# Edition 4.2 — image-free portfolio

09/26/2026. Preserves the technical source code, synthetic datasets and existing screen-development prose. Personal images are omitted from every publication surface, including nested downloadable archives and PDF objects.

The release bundle is assembled from the audited source allowlist, without Python bytecode or cache directories. Embedded downloads are synchronized with their source files. The all-samples archive has its own manifest and excludes the website to avoid recursive packaging.

The Quiet Stage, South Bank, After Hours and Casework: Unknown are written development materials, not professional credits or a showreel. Technical samples remain AI-assisted demonstrations, not production security tools or independent evaluations.

Local validation is not proof of deployment. See VALIDATION.md for the checked scope and limitations.

Title maintenance: **Casework: Unknown** is synchronized across the page, profile, Markdown files, PDF and embedded downloads. The concept itself and both technical demonstrations are unchanged.
