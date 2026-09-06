# Changelog

## v5.1 - Vault Schema Policy (2026-06-21)

- Added `policies/vault-schema.md` — 6 hard rules for Obsidian vault writing (frontmatter mandatory, Mustache quoting, bracket-attach, title-quoting, em-dash in block scalar, template validation).
- Triggered by 2026-06-21 vault sweep (19 violations fixed across 4 owner categories: Scout cron, Hermes actions, Scribe templates/meetings, Documents/IBL Banca).
- All 9/10 team agents acknowledged the policy within 10 minutes of dispatch.

## v5.0 - Operating Repository

- Refactored repository from narrative landing/playbook into structured operating repository.
- Added `docs/`, `agents/`, `policies/`, `configs/` and `evals/`.
- Moved public dashboard source to `docs/index.html`.
- Replaced root `index.html` with redirect to preserve GitHub Page root access.
- Added machine-readable routing in `configs/routing.yaml`.
- Added autonomy, tool, memory, confidence and security policies.
- Added routing, hallucination, delegation and tool-use evaluation cases.

## v4.3

- Narrative public playbook and GitHub Page.
