# Upstream correlation

Issue: https://github.com/openclaw/openclaw/issues/143381

Linux reproduction: https://github.com/openclaw/openclaw/issues/143381#issuecomment-5633564100

The upstream report and VPS evidence agree on the causal chain: isolated heartbeats receive fresh session IDs, materialize MCP runtimes during catalog discovery, do not request run-end MCP cleanup, and retain those runtimes indefinitely when the session idle TTL is zero.

The issue identifies heartbeat-owned run-end retirement as the cleaner upstream correction and a positive idle TTL as the supported operator workaround. Because installed 2026.9.3 does not expose heartbeat-scoped `cleanupBundleMcpOnRunEnd` through supported configuration, upstream evidence reinforced rather than changed the selected 15-minute TTL fallback. No source patch or additional issue-suggested change was applied.
