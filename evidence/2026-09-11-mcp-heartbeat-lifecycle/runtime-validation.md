# Runtime validation

Observer: detached transient systemd unit, two-second samples, 1,025 samples. The transient unit completed and was automatically collected; its final report and raw TSV remained on the VPS.

## Natural heartbeat

- Receipt: `20c23bad-d02a-494b-964d-c5519131fb4b`
- Session key: `agent:cleo:main:heartbeat`
- Session ID: `50fae64e-39a9-4c9d-a8a0-e9daa1a9a151`
- Start: 2026-09-11 11:39:17.651 UTC
- Finish: 2026-09-11 11:39:35.825 UTC
- Status: `ok` / session `done`
- Entire cohort first absent: 2026-09-11 11:54:21.455 UTC
- Continuous absence confirmation completed: 2026-09-11 11:54:51 UTC

## Cohort

All three groups were created by the same heartbeat and had ancestry rooted at Gateway PID 23838:

| Server | Relay | Anchor | Server process |
|---|---:|---:|---:|
| ClawMem MCP | 29193 | 29206 | 29228 |
| Consumer bridge | 29199 | 29220 | 29243 |
| Curator bridge | 29212 | 29227 | 29244 |

## Metrics

| Metric | Before | Peak | After |
|---|---:|---:|---:|
| Gateway processes | 2 | 14 | 2 |
| Gateway tasks | 24 | 76 | 24 |
| Gateway cgroup memory | 1647.512 MiB | 2228.820 MiB | 1700.375 MiB |
| MemAvailable | 4.748 GiB | 4.183 GiB | 4.938 GiB |
| Swap used | 411 MiB | 411 MiB | 390 MiB |
| Relay | 0 | 3 | 0 |
| Anchor | 0 | 3 | 0 |
| Bun | 1 | 2 | 1 |
| Consumer bridge | 0 | 1 | 0 |
| Curator bridge | 0 | 1 | 0 |

Gateway PID was 23838 before and after. Cgroup `oom`, `oom_kill`, and `oom_group_kill` counters were zero before and after.

## Consecutive-heartbeat check

The Cleo session database records ten consecutive heartbeat sessions as `done` from 11:39 through 16:09 UTC, each with a fresh session ID. At the later safety snapshot, Gateway PID 23838 was still active and no relay, anchor, ClawMem MCP, consumer bridge, or curator bridge cohort was present. This confirms the previously deterministic cross-heartbeat accumulation did not recur during the observed five-hour period.

The pre-existing `idrivee2` OAuth warning continued. A separate 12:09 MCP initialization timeout burst occurred during overlapping work, but the associated receipt and heartbeat completed successfully. There is no evidence that idle eviction terminated an active lease.
