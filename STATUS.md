# SYSTEM STATUS

Last update: 2026-09-11
Current task: MCP runtime lifecycle remediation for isolated Cleo heartbeats
Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW
Engineering acceptance: RUNTIME_VERIFIED
Runtime: 15-minute MCP idle TTL reclaimed the observed heartbeat cohort; ten consecutive isolated heartbeats completed and no retained cohort remained
Current Commit: current PR #1 HEAD, resolved after push
Branch: codex/handoff-ledger

V4.1 is listed on OpenRouter, but the sole endpoint is excluded by the existing paid-model-training guardrail. All four model changes were rolled back; Scout primary is V4 Pro 0813 with original Gemini/Sonnet fallbacks and thinking high. No policy relaxation.

Initial test unexpectedly invoked Fable due to missing modelPolicy.allow and installed first-allowed-catalog selection behavior. Preserved as failed acceptance evidence. Repeated 315-second active-work drain timeout and startup handshake degradation are documented.

Latest handoff: handoffs/2026-09-11_1635_mcp-heartbeat-lifecycle.md
Evidence: evidence/2026-09-11-mcp-heartbeat-lifecycle/
The prior Scout routing handoff and pending review remain preserved. No COMPLETE claim before independent review.
