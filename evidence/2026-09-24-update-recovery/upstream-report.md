## Additional observed-state reproduction on 2026.9.6: Doctor changes the retained index, then rejects its identity

Adding evidence to this canonical issue rather than opening a duplicate. This was observed on 2026-09-24 during recovery from a failed **2026.9.5 → 2026.9.6** npm update. It is an observed-state reproduction, **not a clean-install minimal reproducer**. No claim is made that current main was tested.

### Environment and impact

- Native Linux, systemd user Gateway service; Node **24.21.0**.
- Installed and subsequently serving OpenClaw **2026.9.6**, upstream release commit `eb377ac59e6c9fd6c7705028034812becf00271b`.
- Failed update recorded `state-migrated-no-rollback`, `serviceRestartSafe: false`, `runtime-verification-failed`; the Gateway was initially stopped.
- Relevant state: a retained directory belonging to a retired Codex agent, a completed core session import, a `deferred-plugin-session-import` receipt, and pending plugin migration. The Codex plugin was intentionally disabled before repair.
- Supported Doctor/update-repair attempts did not settle this state. Gateway availability was subsequently recovered separately; migration repair remains incomplete.

### Observed sequence

1. The retired agent's `sessions/sessions.json` was missing. Its preserved `sessions.json.migrated-before-v2026.8.x` existed and contained three session entries. The initial failure was:
   ```text
   Deferred plugin session inputs have no verified source index: <retained-agent-path>
   ```
2. After an encrypted backup with verified remote readback, the preserved index was copied byte-for-byte to `sessions.json`. Its SHA-256 matched the retained import receipt. No index entries or receipt values were synthesized.
3. Native repair recognized the verified import and rebuilt the retained source/database binding. During full Doctor repair, the legacy index was rewritten: observed field differences included delivery metadata, `sessionFile`, and `skillsSnapshot` normalization.
4. The same repair then failed with:
   ```text
   Retained session migration source changed: <retained-agent-path>/sessions/sessions.json
   ```
   The diagnostic stated that the verified import was not replayed. The post-session plugin repair was blocked by prerequisite session repair failure.
5. Restoring the original receipt-matching index and running a subsequent full `openclaw doctor --fix --non-interactive` reproduced the changed-index conflict. These repair attempts preceded Gateway activation. We did not capture a syscall trace identifying the exact write function; the attribution is to the observed Doctor repair interval, not a proven function-level trace.

| Artifact | SHA-256 |
|---|---|
| Preserved original / receipt-matching restored index | `ac0cd823da83666b13e3657b5ead456bd8f028f3ece098ce2c7db3782203c3a6` |
| Index after Doctor normalization | `fcc5583d729f8ccd5db0755d77756b3d14dd7895f7a3da11a5d3280fbd56efb3` |

Both generations were preserved in an encrypted backup. The final local index is again the original receipt-matching copy. No raw session index, transcript, database, credentials, or private log payload is attached.

### Repair attempts and boundaries

- `openclaw update repair --no-restart --json --timeout 180`, then a later attempt with `--timeout 300`: did not settle recovery; the first encountered the missing source, and the later attempt reached the retained-source conflict/deadline.
- Full native `openclaw doctor --fix --non-interactive` attempts reproduced the retained-source conflict.
- Native repairs converged seven official plugins to 2026.9.6.
- `openclaw plugins update @openclaw/codex@2026.9.6` successfully replaced a missing managed package generation, but did not clear its pending migration. Its existing disabled configuration was preserved.
- Installed `filterPluginDoctorStateMigrationRecords` excludes non-bundled records that fail `isActivatedManifestOwner`. This is a second state constraint worth reviewing: a pending disabled-plugin migration remains after package restoration. We have not established that it independently causes the index rewrite.
- No receipt editing, migration-completion fabrication, integrity-check bypass, source-code patch, downgrade, or permission widening was used.

### Preservation and runtime checks

All **17 SQLite databases** passed `PRAGMA quick_check`. The three original session IDs and **205 transcript events** were found in canonical migrated stores; original transcript files were preserved. This is integrity/count evidence, not a claim of exhaustive semantic validation. The main configuration hash remained unchanged.

After offline checks, a single atomic `openclaw gateway restart` timed out its readiness command after 242 seconds. The **same process** subsequently passed `openclaw health --json` and `openclaw gateway status --deep`: serving **2026.9.6**, RPC/connectivity OK, no automatic restarts. Fresh `openclaw channels status --probe --json` passed for all eight configured Telegram accounts. No end-to-end delivery test was sent.

CPU/event-loop degradation persisted despite successful RPC. Read-only sampling showed substantial worker CPU, but its causal relationship to this migration defect is **unproven** and is not presented as this issue's root cause.

### Expected behavior / requested investigation

Please investigate the retained-index normalization/settlement ordering in the 2026.9.6 Doctor recovery path. A recovery pass should preserve the verified historical source before normalizing a canonical index, then settle only after validating the relationship between both generations and imported history. Broadly accepting a changed source or rebasing receipts would risk masking unimported data and is not the requested fix.

A useful regression fixture would cover: completed core import + receipt, retired agent index restored from its genuine preserved source, Doctor metadata normalization, and a pending intentionally disabled non-bundled plugin. Assert preservation of both generations and newer SQLite history, no stale replay, and an actionable outcome without requiring plugin enablement or disabling integrity guards.
