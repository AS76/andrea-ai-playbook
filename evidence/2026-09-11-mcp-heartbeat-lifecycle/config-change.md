# Configuration change

Active file: `/root/.openclaw/openclaw.json`

Supported-fix classification: `C — NOT CONFIGURABLE THROUGH SUPPORTED CONFIG` for heartbeat-scoped `cleanupBundleMcpOnRunEnd` on installed OpenClaw 2026.9.3.

The only production configuration change was:

```diff
 "mcp": {
+  "sessionIdleTtlMs": 900000,
   "servers": {
```

Installed schema accepts a finite number greater than or equal to zero. Installed runtime documentation states that unset or zero disables idle eviction and that active leases and pending acquisitions prevent eviction. The manager uses an approximately 60-second sweep interval and skips runtimes with an active lease or a pending runtime work chain.

`gateway.reload.mode` was `off`, so one controlled user-service restart was required. The old process drained for the configured 315-second interval and shut down cleanly. The replacement Gateway became ready at 11:16:48 UTC with PID 23838 and passed its health RPC. No second lifecycle change was applied.
