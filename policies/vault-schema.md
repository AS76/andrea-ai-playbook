# Vault Schema Policy

**Status:** Active — locked 2026-06-21
**Source of truth:** `vault/Projects/VAULT-SCHEMA.md` v1.1.1 (Obsidian canonical)
**Hard rule:** Yes (non derogable)
**Owner:** Cleo (governance) + Scout (validator) + tutti gli agenti scrittori (compliance)

---

## Scope

This policy applies to:

- **In scope:** every `.md` file under `/root/.openclaw/workspace/main/vault/` (Obsidian vault)
- **In scope:** every `.md` file emitted by any agent into the vault, via cron, script, or manual write
- **Out of scope (today):** bootstrap context files under `/root/.openclaw/workspace/<agent>/` (e.g. `SOUL.md`, `IDENTITY.md`, `MEMORY.md`) — see § Scope Open Questions below
- **Out of scope:** `shared-knowledge/*.md` files (sync files, briefs) — use plain markdown format with `# Agent sync — YYYY-MM-DD HH:MM UTC` h1 per `sync-nudge.sh` convention

## The 6 hard rules

These rules are derived from VAULT-SCHEMA.md v1.1.1 + lessons learned during the 2026-06-21 vault sweep (19 violations fixed across 4 owner categories).

### 1. Frontmatter YAML mandatory with `type` + `tags`

Every `.md` file in the vault MUST have YAML frontmatter with at minimum `type` and `tags`. Missing `type` is a schema violation.

### 2. Mustache `{{...:...}}` → always quoted

YAML mustache placeholders containing `:` (e.g. `{{date:YYYY-MM-DD}}`) break the parser. Always write `'{{date:YYYY-MM-DD}}'` (single-quoted) in frontmatter.

Note: mustache in markdown body (e.g. `# {{date:YYYY-MM}}`, lists `Daily/{{monday:YYYY-MM-DD}}`) is OK without quoting — Templater expands them at runtime, not YAML.

### 3. `]` or `}` attached to closing `---` → always newline before

Never write `]---` or `}---`. Always insert a newline: `]\n---`. This is a silent YAML failure that passes naive regex but breaks parsers.

### 4. `title: <number> <text>` → always quoted

When a title starts with a number or date and contains `:` or spaces, quote it. Example: `title: "06-03 Site Operational Discipline Breakdown"`. Unquoted versions parse but break tooling that expects a YAML scalar.

### 5. Block scalar `|`: em-dash instead of `:` when list value may confuse the parser

In `block scalar |` contexts, prefer em-dash (`—`) over colon (`:`) in list-item values when indentation is ambiguous. The parser may interpret `:` as a key separator in adjacent context.

### 6. Original templates must be validated before use

Any template in `Templates/` (or anywhere else) that gets used to generate vault files must be validated end-to-end before being merged or reused. A bug in a template propagates to all children.

`Templates/Action.md`, `Templates/Monthly-Review.md`, `Templates/Risk.md`, `Templates/Weekly-Review.md`, `Templates/Decision.md` were all bugged on 2026-06-21 (mustache + missing `---` close). They are now fixed; do not regress.

## Type taxonomy (current)

Observed `type` values in the vault (post-2026-06-21 sweep):

| Type | Count | Owner |
|---|---|---|
| person | 92 | various (people cards) |
| daily | 37 | Scout cron + manual |
| knowledge | 18 | Scribe + others |
| action | 14 | various (mostly Hermes) |
| project-index | 9 | Scribe |
| decision | 7 | Atlas + Scribe |
| meeting | 7 | Scribe (Plaud pipeline) |
| weekly-review | 5 | Scribe |
| monthly-review | 2 | Scribe |
| template | 2 | Scribe (OOO) |
| risk | 2 | Atlas |
| risk-analysis | 2 | Atlas (note: not canonical, see open question) |
| document | 1 | various |
| schema | 1 | this document |

**Open question:** `risk-analysis` is used by Atlas for long EMA5 risk reports, vs `risk` for short files in `Risks/`. VAULT-SCHEMA does not specify a closed set of allowed `type` values. If canonicalization is desired, rename to `risk-report`.

## Detection and enforcement

- **Detector script:** `python3 /tmp/scanner_violations.py` (reusable). Scans 238 files in <2s. Reports `no-type`, `no-frontmatter`, and `parse errors`.
- **Extended detector (Scribe):** `/tmp/scribe_vault_audit.py` — adds 3 checks: Mustache-in-fm, title-number-not-quoted, bracket-attach.
- **Cron (planned):** `vault-lint-daily` 23:50 Europe/Rome (21:50 UTC) — pre-`scout-daily-log` safety net. Pending Cleo approval.
- **Pre-commit hook (planned):** block creation of new non-conformant files. Pending Cleo approval.

## Owner responsibilities (one-liner)

| Agent | Vault scope | Self-check before emit |
|---|---|---|
| Scout | Daily, MEMORY sync, briefings | ✓ |
| Cleo | AGENDA, governance, syncs | ✓ |
| Atlas | Decisions, Risks | ✓ |
| Max | Knowledge, scripts output | ✓ (in scope only) |
| Scribe | Templates, Meetings, Decisions, Documents | ✓ (heaviest contributor) |
| Pixel | Design notes, visual concepts | ✓ |
| Mark | GTM, positioning, persona, channel-plan | ✓ |
| Counsel | Decisions, Risks (rare) | ✓ |
| Lex | Contracts, legal review (mostly outside vault) | ✓ |
| Visa | Passport, UKVI, travel docs | ✓ |
| Tutor | (out of vault — workspace only) | N/A |

## Open questions (require Cleo / Andrea decision)

1. **Scope extension to bootstrap context:** does the rule apply to `workspace/<agent>/SOUL.md`, `IDENTITY.md`, `MEMORY.md`? Adding YAML frontmatter there may break OpenClaw's bootstrap parser. **Default today: no, but a parallel compliance check for bootstrap files is recommended.**
2. **`risk-analysis` taxonomy:** rename to `risk-report` for canonicalization, or accept as-is?
3. **Cron `vault-lint-daily`:** approve scheduling, or keep manual?

## Lessons learned (one-liner)

The 2026-06-21 sweep (Scout + Hermes + Scribe) fixed 19 files across 4 owner categories:

- 4 Daily (Scout cron systemic bug — now fixed in template)
- 4 Actions (Hermes 17/06, bracket-attach)
- 4 Templates originals (Scribe, mustache + missing close)
- 3 Templates OOO (Scribe, no frontmatter)
- 2 Meetings (Scribe, title-number not quoted)
- 1 Decision (Scribe, block-scalar `:`)
- 1 Documents/IBL Banca (no type)

**Lesson:** every owner of a cron or template that emits vault files MUST run `vault-lint` after the first emit, and before scaling. Silent YAML failures (mustache, bracket-attach) are invisible to regex-based detection.

## Provenance

- **Trigger:** Andrea directive 2026-06-21 16:48 UTC
- **Source violation report:** Hermes vault scan 2026-06-21 16:29 UTC (msg 6613)
- **Detector recipe:** `/root/.hermes/skills/note-taking/obsidian/references/schema-violation-detector.md`
- **Sweep completion:** 2026-06-21 16:42 UTC by Scout
- **Ack from 9/10 team agents:** 2026-06-21 16:53–16:57 UTC
- **Backup:** `/tmp/vault-backup-20260621-1642/`
