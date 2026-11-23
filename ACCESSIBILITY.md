# Accessibility — Research Portfolio

**Status:** Initial public accessibility statement; evidence-limited  
**Last reviewed:** 11/23/2026  
**Owner:** Stephan Szwaj  
**Scope:** The [public research portfolio website](https://kingstephan18.github.io/research-portfolio/) and the user-facing documentation of [`KingStephan18/research-portfolio`](https://github.com/KingStephan18/research-portfolio).

## Commitment and goals

The portfolio aims to make research evidence, technical examples, and screen-development material understandable and usable by people with different input methods and assistive technologies. Accessibility is considered during changes to navigation, content, interactive controls, and downloadable materials.

This statement **does not claim conformance** with any Web Content Accessibility Guidelines (WCAG) level. A complete accessibility evaluation has not been documented.

## Measures visible in the current source

The repository's `index.html`, inspected on 11/23/2026, includes:

- A *Skip to content* link targeting the page's main area.
- Semantic `header`, `nav`, `main`, and `footer` landmarks, together with labelled navigation.
- Text alternatives for some decorative or explanatory elements, and header cells in at least one table.
- A CSS rule responding to the `prefers-reduced-motion` preference.

These are **source observations**, not proof that every interaction works with a screen reader or keyboard.

## Environments and evaluation status

The repository's `VALIDATION.md` reports a staged Chromium rendering review dated 10/24/2026 at desktop, tablet, and phone sizes, with no horizontal overflow or JavaScript errors in the tested views. That was a **responsive/browser check**, not an accessibility conformance assessment. It does not establish live-site or cross-browser conformance.

**Not verified as of this review:** complete keyboard-only navigation (including filtering and downloads); screen-reader behavior (NVDA, JAWS, VoiceOver, TalkBack); focus visibility and order across all interactions; color contrast across every state; text zoom/reflow and browser-specific behavior; accessibility of downloadable PDF/ZIP material and externally linked resources. These are evidence gaps, not a claim that all such features are defective.

## Known barriers and limitations

No comprehensive accessibility audit or confirmed issue inventory was available during this review. Consequently, we cannot assert that no barriers exist or promise that all experiences are accessible. Interactive examples, the horizontally scrollable record comparison, and archived downloads should receive particular attention in future testing.

As barriers are verified, describe the affected task and environment, provide available workarounds, and link to documented remediation work. Do not describe an untested behavior as a confirmed defect.

## Reporting an accessibility barrier

**Report a barrier using [GitHub Issues](https://github.com/KingStephan18/research-portfolio/issues/new)** in this repository. GitHub Issues was enabled by the repository owner and verified through a fresh GitHub API read on 11/23/2026. If possible, begin the issue title with `Accessibility:` so the report is easy to locate. GitHub sign-in may be required to submit an issue.

Please describe the affected page or task, what happened and what you expected. Helpful but optional details include browser, device, operating system, input method, and assistive technology (if any). **Do not disclose a disability, medical history, private data, screenshots or recordings unless you choose to; none is required.** Do not include passwords, tokens or other secrets.

The maintainer will review reports when possible, identify the affected experience, note verified limitations and workarounds, and track corrections through the appropriate issue. No guaranteed acknowledgement time, resolution time or continuous support coverage is claimed.

## Contributor and AI-agent expectations

For meaningful user-interface changes:

1. Preserve semantic structure, descriptive links, and labelled controls; avoid relying on color or spatial placement alone.
2. Check the affected task using keyboard-only navigation and, when relevant and feasible, a screen reader.
3. Inspect zoom/reflow, focus states, motion preferences, and responsive layouts.
4. Describe actual test environments, methods, dates, results, known gaps, and relevant workarounds. Do not equate automated linting or responsiveness with verified WCAG conformance.
5. Never invent completed testing or accessibility guarantees. Changes to external settings or publication require the owner's authorization.

## Ownership and maintenance

The repository owner maintains this statement. Revisit it when meaningful interface or accessibility-related changes occur, and retain dates and evidence for any verified claims. No guaranteed acknowledgement or remediation deadline has been established.

---

**Version and evidence:** Initial statement prepared 11/23/2026 from the current public source and its documented validation history. Source and test evidence should be updated whenever the affected implementation is independently evaluated. The repository’s `SHA256SUMS.txt` manifest covers this file for integrity checking; it does not certify accessibility.