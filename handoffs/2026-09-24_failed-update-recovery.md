# CODEX HANDOFF

## Metadata

Date: 2026-09-24
Component: local OpenClaw update recovery
Codex Status: PARTIAL
Runtime Verification: PARTIAL
ChatGPT Review: PENDING_REVIEW
Commit: codex/recovery-20260924
Branch: codex/recovery-20260924

## Request and initial state

Repair failed update 058bf830-7c45-43a1-88fa-2ca6802b0ec9 while preserving configuration, migrated state, databases and history. The requested environment named 2026.9.5; live CLI and the service target were already 2026.9.6 (eb377ac), Node 24.21.0. Service inactive; RPC refused. No rollback or manual stop was performed.

## Confirmed findings

The recorded update failed after migration, with no verified rollback. Its session migration target was a retired Codex agent directory: three original transcripts existed, but sessions.json existed only under a historical migrated suffix. The disabled Codex plugin also referenced a missing managed package directory. Eight official plugins had version drift.

The initial plain Doctor invocation unexpectedly completed 17 deferred plugin migrations before the first S3 backup; subsequent explicit repairs ran only after verified backup. Advisory Doctor JSON reported 35 checks, 30 skipped and no findings, while health and RPC failed. This advisory result did not establish recovery.

## Actions and evidence

- Four encrypted S3 streams passed producer/encryption checks and complete remote SHA-256 readback. No archive bundle was staged locally by these backup producers. Restore/decryption not tested.
- Restored original retired-agent sessions.json byte-identically. Three IDs matched database history and all original transcripts existed. Targeted migration dry-run validated three entries and 205 events.
- First native update repair reproduced blocked-by-session-repair-failure. Native service reconciliation changed Unit.StartLimitBurst, Unit.StartLimitIntervalSec and Service.KillMode; operator drop-in preserved.
- Second native update repair verified canonical import, retained source inputs for deferred plugins, then refused an index hash conflict. The index changed from the verified original hash to normalized content during Doctor, and the command reached its 300-second deadline. Cancellation settled before recovery. No receipt or verification guard was edited.
- Preserved the conflicting index/database on S3 and restored only index content whose SHA-256 matches the recorded migration receipt. Started native doctor --fix --non-interactive.
- Native Doctor migrated the retired hidden directory into canonical agent storage. The three original session IDs still have 205 transcript events in canonical stores; source JSONL files remain.

## Backup manifests

| S3 key under maintenance/2026-09-24/ | SHA-256 |
|---|---|
| update-repair-058bf830-prechange.tar.gpg | ed783c3263b0876c59eaeb2e09b6780a6577a7f4c9b5230251856b612a392e01 |
| update-repair-058bf830-session-sources.tar.gpg | 7f4ff3a8e0e04eedbbbd40449b868d99117b6ee1ea573fec8eeea13511216a20 |
| update-repair-native-service-artifacts.tar.gpg | 1207b8100809f26bcd39e07207fef2be1ac115cc59039b900e23b5e7af52f74f |
| update-repair-session-conflict.tar.gpg | d252b2adbf84401c72d9eb1ce2c86cbec3058750a116ff48b8a521ede33a3e40 |

## Risks and limits

Native repair automatically created local service/config backup files despite the S3-only operational policy. Service artifacts were subsequently streamed encrypted to S3; local originals were retained for safety, so this is a disclosed policy deviation. No manual deletion was performed. A later native Doctor pass reclaimed 43 temporary plugin capture roots (435 MB), then stopped cleanup when its live-process census could not establish ownership.

Original main configuration SHA-256: ec0a66a5e4417fe43b9a24ecb0b13fb50d0228611aac24f9fc584602f6878cf4. Matching hash reconfirmed after both update-repair attempts. No model/provider/OAuth change intended.

## Pending verification

Native Doctor remains blocked by retained-source normalization conflict; Gateway service restoration verified separately. Overall acceptance is PARTIAL / DEGRADED, not full recovery.

## Direct Doctor progress

Native Doctor rebuilt the verified retained source index and database binding from its own receipt, without replaying canonical SQLite sessions. Deferred plugin list reduced to Codex only. Native Doctor updated deepseek, lobster, mistral, moonshot, perplexity, slack and voyage from 2026.9.4 to 2026.9.6. Old plugin generations were retained until Gateway activation, which later reclaimed them. Canonical Codex and retired-agent databases passed quick_check; the same three session IDs retain 205 events.

## Final offline checks and remaining defect

The Codex package was reinstalled using `openclaw plugins update @openclaw/codex@2026.9.6`; exit 0 and installed index confirm the new package path/version. The plugin remains disabled. A subsequent full native Doctor still reproduced the retained-source mismatch. After Doctor exited, the index was restored again from the original whose hash matches the migration receipt; normalized content was already preserved in the verified S3 conflict archive. No receipt, lock, approval or schema guard was modified.

Configuration validates with only the deferred Codex warning. All 17 local OpenClaw SQLite databases pass quick_check. Plugin diagnostics report zero pluginErrors but overall ok=false due warnings: context-vault and composio before_prompt_build hooks lack allowConversationAccess approval, and Codex migration remains pending. No capability widening was accepted.

Native `openclaw gateway restart` invoked only after offline checks. No separate stop/start command was used; no subsequent operator stop was observed before invocation. Runtime verification follows.

## Runtime outcome

Atomic restart exited 1 after a 242-second readiness deadline with channel-probe timeouts. Its same PID 4030781 subsequently settled: health RPC succeeded twice (483 and 498 ms), gateway status --deep confirms version 2026.9.6 and connectivity ok, readyz returned HTTP 200, and the listener queue drained to zero. Systemd automatic restart count is zero. The serving version matches the installed update target and upstream v2026.9.6 commit eb377ac59e6c9fd6c7705028034812becf00271b; it does not match the supplied pre-update 2026.9.5 expectation.

Eight configured Telegram accounts report running and connected with no lastError; fresh `openclaw channels status --probe --json` probes passed for all eight (174–871 ms). Slack is unconfigured, not a required connected channel. No test message was sent. Health plugins.errors and plugins.unavailable are empty; modelRuntime is not degraded.

Remaining failures are explicitly retained: eventLoop.degraded=true for CPU, 82 failed outbound delivery records (oldest timestamp predates this update), disabled Codex migration pending, and context-vault/composio conversation-access hook warnings. Brave remains at its available registry release 2026.9.5; no 2026.9.6 release was available to converge. No queue records were deleted or resent. Gateway activation natively reclaimed seven previously retained managed plugin generations.

## Recommended next action and review

Review the native Doctor index-normalization/retained-source conflict with the Codex plugin migration owner before further maintenance. Do not edit receipts or replay verified imports, blindly roll back migrated state, enable disabled Codex, or widen hook permissions as a shortcut. Preserve original and normalized index versions in the verified S3 archives. Separately investigate ongoing CPU pressure and failed-delivery backlog without resending private messages automatically.

Review requested: assess preservation, native repair side effects, startup/runtime evidence, residual blockers and policy deviations. Evidence: evidence/2026-09-24-update-recovery/verification.json. This handoff claims partial service restoration only.

## Follow-up: force repair versus reset

Read-only 10-second thread sampling attributed approximately 43% and 27% of one CPU core to two worker threads, versus 15% to the main thread. A separate 10-second perf capture collected 743 samples with zero lost samples; prominent symbols were V8 object property/prototype and WeakMap operations. This establishes worker CPU activity, not a definitive JavaScript function or root cause. A runtime memory warning identified the prepared-model-catalog worker as the largest worker heap (approximately 702 MB); mapping that worker to the hot OS thread remains unproven. RPC health still succeeded in 1042 ms with modelRuntime healthy and CPU degradation retained.

Installed Doctor source explicitly excludes inactive non-bundled plugins from state migrations. Codex remains intentionally disabled, so reinstalling its missing package alone cannot finish its deferred migration. The retained-source normalization conflict is separate and reproducible. No receipts, capability approvals, plugin enablement, runtime code, or model routes were changed during this follow-up. No reset is justified by the observed database checks and working RPC/channel probes. Forced bypass would not constitute verified recovery.

## Upstream report published

User authorized reporting to OpenClaw. Existing canonical issue #154679 covers the retained-index conflict; #156016 was already closed as its duplicate. Published the sanitized 2026.9.6 observed-state reproduction at https://github.com/openclaw/openclaw/issues/154679#issuecomment-5809162098. Verified the fetched comment body matches the reviewed local report. Included source hashes, native repair results, database/runtime checks, uncertainty about the exact write function, and a proposed regression fixture. CPU remains explicitly separate and causally unproven. No private payloads or raw artifacts published; no runtime changes for this reporting task.

## Consolidated daily report and latest availability check

This handoff consolidates the recovery, CPU follow-up, upstream publication, and subsequent usability check performed in this session on 2026-09-24. It does not claim coverage of unrelated operations by other agents today. User explicitly requested the complete report in ClawMem and the Codex ledger.

Latest `openclaw health --json` completed successfully in 1572 ms. All eight Telegram accounts were running and connected with lastError null; modelRuntime.degraded=false and pendingAgents empty. Event-loop degradation persisted: reasons event_loop_delay, event_loop_utilization and cpu; delay p99 1451.2 ms, utilization 1, CPU core ratio 1.103, main-thread ratio 0.213, host utilization 1 on two CPUs. These are a snapshot, not sustained service-level guarantees.

The paired `openclaw gateway status --deep` again confirmed serving version 2026.9.6, PID 4030781 and connectivity probe ok. It also warned that service PATH lacks /root/.local/share/pnpm, Codex settings cannot be fully checked before pending migration completion, and Brave has no matching 2026.9.6 registry release. No automatic PATH rewrite or service reinstall was performed. Sanitized evidence: evidence/2026-09-24-update-recovery/latest-availability.json.

Operational answer: OpenClaw is available for use, with possible latency/timeouts under the observed CPU pressure. Availability is verified; full reliability and an end-to-end model response/message delivery were not verified. Retained-source repair remains incomplete. Do not infer successful maintenance from top-level health ok, connected channels, or database quick_check alone.

Remaining work: obtain a data-preserving upstream fix for retained-source normalization/settlement; resolve disabled Codex migration through supported lifecycle semantics; investigate worker CPU without assigning an unproven root cause; assess failed-delivery backlog without automatic resends; review service PATH warning and intentional plugin hook permissions separately. No wipe/reset, forced receipt update, capability expansion or blind repeated Doctor passes are justified by current evidence. Engineering outcome remains PARTIAL / DEGRADED; independent review PENDING_REVIEW.
