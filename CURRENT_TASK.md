# CURRENT TASK

Request: verify V4.1 Flash on OpenRouter, replace Scout V4 Pro if usable, test functionality; explain unexpected Fable selection.
Overall status: REVIEW_REQUIRED
ChatGPT Review: PENDING_REVIEW
Engineering acceptance: BLOCKED_PROVIDER_GUARDRAIL

Outcome: public catalog availability confirmed, actual provider request rejected by account paid-model-training guardrail. All model changes rolled back to V4 Pro 0813. Gateway ready 08:39:14Z; health RPC PASS (86ms).

Initial Fable test: failed requested-model acceptance; missing modelPolicy.allow led installed resolver to first allowed catalog entry. Evidence and operator omission preserved. Exact policy addition corrected selection, but provider guardrail still blocked inference. No guardrail relaxation or broader routing modification.

Handoff: handoffs/2026-09-10_0812_scout-v41-flash.md
Evidence: evidence/2026-09-10-scout-v41/
Review target: current PR #1 HEAD; exact SHA to verify after push.
Remaining: independent review. Future migration needs a compatible provider endpoint or separately authorized account-policy decision.
