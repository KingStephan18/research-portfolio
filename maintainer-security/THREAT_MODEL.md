# Cross-border software-supply-chain threats — maintainer research note

**Research baseline: 10/21/2026.** Scope: open-source maintainers, third-party Actions, automated code review and software releases. This is a bounded research/practice note, **not** a claim that all countries have the same incidents, nor an incident alert or attribution report.

## Verified threat picture

ENISA's *Threat Landscape 2026* (released 09/22/2026, assessing events from 2025) highlights ransomware's short-term impact, DDoS activity against public entities, geopolitical cyberespionage and the expanding attack surface from interdependencies. These are **separate categories**, with different defenses. ENISA's EU analysis should not be incorrectly described as a worldwide incident census.

OpenSSF's 06/11/2025 technical guide documents the `tj-actions/changed-files` and `reviewdog/action-setup` supply-chain compromises. In its account, access and mutable action tags were used to propagate malicious code to CI workflows and expose secrets. This demonstrates why a maintainer's CI/CD security can matter beyond one repository. GitHub's secure-use guidance warns against privileged workflows executing untrusted PR content and recommends fine-grained `GITHUB_TOKEN` permissions and pinned Actions. Sources: [ENISA](https://www.enisa.europa.eu/publications/enisa-threat-landscape-2026), [OpenSSF](https://openssf.org/blog/2025/06/11/maintainers-guide-securing-ci-cd-pipelines-after-the-tj-actions-and-reviewdog-supply-chain-attacks/), [GitHub](https://docs.github.com/en/actions/reference/security/secure-use).

## Threat-to-control map

| Threat path | What the maintainer should verify | This repository's evidence |
| --- | --- | --- |
| Compromised or retagged GitHub Action | Review source/publisher, pin full commit SHA, monitor updates | `workflow_review.py` flags ordinary mutable references; it cannot verify the pinned source. |
| Untrusted PR material used in privileged jobs | Separate trusted and untrusted workflows; never execute fork code with privileged secrets | Heuristic trigger/ref checks; not data-flow analysis. |
| Token or credential misuse | Minimize scopes, restrict secrets, use ephemeral credentials, rotate after exposure | Flags explicit `write-all` and missing conventional permission key; does not inspect secrets or actual settings. |
| Agent follows malicious instructions in PR/issues | Treat PR text and tool output as data; independently authorize side effects | Existing Permission Boundary Lab demonstrates deny-by-default decisions on synthetic fixtures. |
| Tampered release artifact / malicious dependency | Review transitive dependencies, reproducibility, provenance/signatures, SBOM, response plans | Existing SHA-256 listing is a local integrity aid **not** an authenticated signature or complete dependency audit. |
| Ransomware, phishing, DDoS, cyberespionage | MFA/passkeys, recovery backups, segmentation, monitored access, coordinated response | Outside these demonstrators; no coverage or protective guarantee is claimed. |

## Readiness and incident discipline

1. Identify trusted maintainers, release automation, repositories, dependencies, runners and privileged accounts. Maintain recovery access and least privilege.
2. For any suspicious PR or dependency update, avoid running untrusted code in a privileged context; verify publisher, provenance, requested scopes and exact diff.
3. If compromise is suspected, preserve logs and hashes, isolate affected runners/tokens, rotate exposed credentials, assess published artifacts and downstream reach, and use appropriate private disclosure and incident-response channels. Do not publish working exploit details or private information in issues.
4. Reproduce test results with clean fixtures, record date/version/limitations and seek independent review before claiming robust protection.

## Boundaries and next decisions

`research-portfolio` is a mixed research and screen-work showcase, not currently a broadly adopted cybersecurity product. The new offline checker is an **additional prototype**, not a replacement for OpenSSF Scorecard or CodeQL. Do not inflate stars, adoption, certifications, impact, CVE coverage or security assurance in grant applications. No existing private operational, genealogical or medical systems are included. No automatic deployment, scheduled monitoring, repository permission change, new public repository or blanket content-license grant is authorized by this note.
