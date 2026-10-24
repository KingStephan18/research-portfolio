# Stephan Szwaj
## Research & screen performance

I investigate systems, evidence and human identity. Cybersecurity is my technical priority; AI supports the work. My screen practice draws on classical text, physical comedy and close observation.

### Active cybersecurity research — 10/24/2026

I lead **CYBERSECURITY — INTELLIGENCE & RESPONSE**, an active independent research project combining vulnerability intelligence, review of public GitHub-hosted source code, and evidence-led investigation of potentially unreported security weaknesses. AI/Codex supports analysis and documentation; I direct the work and review its conclusions.

**[Read the current research overview and 10/21–10/24 progress log](security-research/README.md)** — recent PHP and Node.js advisory research, source-review progress, evidence standards and the next validation milestones.

**[Inspect Maintainer Workflow Review](maintainer-security/README.md)** — the published offline GitHub Actions review tool, with source, synthetic tests and an explicit threat model.

I submitted this repository with my **Codex for Open Source application on 10/21/2026**. Submission is recorded; selection or funding is not claimed. The public research page separates inspectable work, maintainer-reported progress and upstream vulnerabilities discovered by other researchers.

### Two paths

**[Research and technical samples](#research-and-technical-samples)** — runnable demonstrations, a transparent synthetic case and method notes.

**[The Quiet Stage](acting/profile.md)** — my self-directed screen-practice profile and two existing written development pieces. [Read the screen portfolio PDF](acting/Stephan_Szwaj_Screen_Portfolio.pdf).

### Research and technical samples

| Work | Inspect | Status |
|---|---|---|
| [Maintainer Workflow Review](maintainer-security/README.md) | Offline review of selected GitHub Actions supply-chain risks | Published Python tool and synthetic tests |
| [Current cybersecurity research](security-research/README.md) | Research scope, dated progress and primary-source advisory notes | Active research / public progress record |
| [Permission Boundary Lab](case-studies/permission-boundary.md) | Exact-scope authorization, expiry and revocation checks | Executable security-decision lab |
| [Evidence Ledger](case-studies/evidence-ledger.md) | Strict JSON parsing, source-origin checks and warning states | Executable reference checker |
| [Same name, different people](case-studies/same-name.md) | Six invented records, competing identities and an unresolved discrepancy | Synthetic research exercise |
| [FRAME 17](case-studies/frame-17.md) | A treatment and scene about a persuasive reconstruction | Unproduced fiction concept; separate from acting credits |

### Screen development material

**[South Bank, After Hours](acting/south-bank-after-hours.md)** — a non-verbal performance study: two strangers, one bench, a choice to stay.

**[Casework: Unknown](acting/casework-unknown.md)** — a paranormal / deadpan-comedy series concept.

The screen section contains existing development writing from the supplied portfolio, edited for this edition. No showreel, completed shoot or professional acting credit is asserted. [Screen provenance](acting/PROVENANCE.md).

### Inspect or run

The standalone `index.html` contains the presentation and embedded downloads. The GitHub file view displays source, not a hosted site. The source package includes the actor dossier and the preserved technical work.

With Python 3.10+ syntax support, run from this directory:

```sh
python verify.py
```

Python 3.13.5 was exercised in the build environment. See [validation](VALIDATION.md), [method](methodology/research-method.md), [sources](SOURCES.md) and [contributions](CONTRIBUTIONS.md).

Edition 4.2 · 09/26/2026. Supplied screen-development material and new AI-assisted demonstrations are distinguished throughout. No employer, studio, school or agency affiliation is implied.

[GitHub profile](https://github.com/KingStephan18)

### Security research extension — 10/21/2026

A new [Maintainer Workflow Review](maintainer-security/README.md) Python sample checks selected GitHub Actions supply-chain risk patterns **offline and read-only**. Its [threat model](maintainer-security/THREAT_MODEL.md) connects concrete maintainer controls with ENISA's 2026 threat picture and documented OpenSSF/GitHub guidance. It is a limited, author-tested heuristic checker, **not** a vulnerability detection service or evidence of a real-world security improvement.

Run `python -m unittest discover -s maintainer-security -v` for the new synthetic tests. To inspect workflows under a local repository, use `python maintainer-security/workflow_review.py /path/to/repository`. A missing workflow directory produces `NOT_ASSESSED`, not a safety claim. This extension is maintained as repository source only; it has not been inserted into the frozen edition 4.2 downloadable portfolio package or released as an independently licensed project.
