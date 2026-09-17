# Model selection root cause
OpenClaw 2026.9.3 installed source:
- dist/agent-command-C9QUtzmi.mjs:2013-2027 calls visibilityPolicy.resolveSelection and assigns the returned provider/model before inference.
- dist/model-selection-shared-T-i8X-YJ.mjs:1067-1084: resolveAllowedModelSelection returns the current model when authorized; otherwise returns allowedCatalog[0]. This does not follow Scout model fallbacks and does not fail closed when another allowed model exists.
- First live probe selected anthropic/claude-fable-5; terminal receipt requested=effective, rerouted=false; successful exec tool. This is NOT V4.1 acceptance.
- Explicit V4.1 probe rejected before inference by agents.defaults.modelPolicy.allow.
- Added exact V4.1 reference to the existing allowlist. No wildcard/removal of restrictions.
- Offline resolver test with configured catalog only: before fix chose first allowed model (Mistral Large in this limited catalog); after fix chose openrouter/deepseek/deepseek-v4.1-flash. Offline test proves selection mechanics, not the live full catalog ordering.
- Root cause includes operator omission of new modelPolicy.allow when adding the model; existing defaults.models entry alone was insufficient.
