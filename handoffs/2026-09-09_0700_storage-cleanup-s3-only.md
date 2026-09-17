# Storage cleanup and S3-only operational backups

## Metadata

Date: 2026-09-09
Host: production VPS
Component: storage lifecycle, encrypted S3 backup pipelines
Codex Status: PASS_WITH_ACTIONS
Runtime Verification: PASS for scoped storage/backup checks; existing unrelated degradation retained
ChatGPT Review: PENDING_REVIEW
Commit: current PR #1 HEAD, exact SHA verified after push
Branch: codex/handoff-ledger
Related issue/PR: AS76/andrea-ai-playbook#1
Related ClawMem context: technical diary #16950 and local maintenance manifests
Evidence: ../evidence/2026-09-09-storage-s3/

## Request and result

The user authorized moving nonessential files to S3 while preserving OpenClaw and its extensions, with Claude Code/Hermes removal only if necessary. During execution the user additionally required every new backup to target S3 without VPS archive storage. Disk occupancy fell from the observed 82% baseline to 62%, about 39 GB available. Hermes and Claude Code were retained; no package removal or application-service restart was necessary.

Cold groups included the complete pre-update state tar, previous update runs, old plaintext and encrypted nightly backups, npm/build caches, desktop trash, downloaded Drive copies, historical configuration/project backup copies, retired-agent archives, abandoned bridge venv, package-manager backup history and already-installed runtime download packages. Canonical Vault, active SQLite/PostgreSQL state, credentials, live model/browser dependencies, OpenClaw extensions and installed runtimes were retained. No claim is made that every unidentified filesystem item was proven unnecessary.

## Authorization, encryption and source removal

Each cold group was encrypted with a random per-group passphrase held in process memory. Its recovery passphrase was separately encrypted to the established offsite recovery public key. S3 object and sealed-key bytes were read back. The complete encrypted object was hashed, decrypted and tar-compared against the original sources before removal. Source stat/identity and open-file/cwd guards were rechecked before exact-path deletion. No unsupported socket entries were found. Cache base directories were recreated empty where appropriate. Three already-encrypted nightly bundles were fully read back and matched against both local and remote checksum sidecars before removing local copies.

The initial plaintext-nightly and pre-update migration batches used temporary local ciphertext. The stricter S3-only instruction arrived while the pre-update batch was in flight; that batch completed verification, then an intentional manifest guard stopped the next batch before creation. All remaining archive batches were switched to multipart streaming, with no local archive. The intentional stop is not concealed as a failed migration: no subsequent group source was removed at that stop. All temporary ciphertext was removed after successful verification; zero staging/nightly archive files remained at final checks.

Restore pointers and restricted manifests remain at /root/storage-s3-maintenance/20260909, with a pointer beside the assisted-update activation notes. The live Node/core installations and source checks remain local. The old core state backup is now offsite: restoring it requires S3 and the established offsite private key. Immediate offline local rollback is deliberately no longer available under the user's S3-only requirement. Data-compatible rollback remains necessary after SQLite schema migration. This run verified decryption with in-memory archive keys, but did not retrieve or test the offsite private key anew.

## Future backup pipelines

1. /usr/local/bin/openclaw-s3-stream.py runs a producer into GPG encryption and multipart S3 upload, with no archive file on VPS disk. Producer/encryption failure aborts incomplete uploads. Successful completion requires full remote SHA-256 readback and checksum/manifest publication.
2. The nightly entry point retains its existing 02:00 schedule. The new producer streams canonical config/documents, consistent read-only SQLite backups held in RAM, and PostgreSQL custom dumps held one at a time in bounded RAM. SQLite quick_check must pass; missing/changed required sources or failed dumps fail the job. The wrapper uses a lock and writes only a small success/failure health marker locally.
3. Vault Daily pruning streams encrypted JSON to S3 and verifies upload before deletion. A changed source aborts deletion. The old local archive-dir argument is retained only for CLI compatibility and is ignored for storage. Production pruning was dry-run only; no Daily file was deleted by this task.
4. APT/dpkg system service drop-ins provide service-private RAM at /var/backups and a wrapper that runs the existing vendor command then streams its backup results to S3 in the same process namespace. They do not alter vendor scripts, package-update policy or schedules. A failed S3 operation does not fall back to disk. The RAM scratch mount is capped at 32 MiB; if backup metadata outgrows it, revise that explicit bound. Existing package transactional state remains on disk because it is live operational state, not a cold archive.
5. Root and workspace AGENTS now require S3-only operational backups and instruct agents to adapt tools that insist on local archives before using them. Arbitrary third-party programs are not globally sandboxed against every possible backup write; verified coverage is the discovered automatic backup paths plus the operational policy.

The system manager was daemon-reloaded to load three drop-ins. OpenClaw and Hermes were not restarted. A real dpkg backup and a synthetic namespace test ran; APT update/install commands were not invoked for testing.

## Validation

- Live nightly backup: PASS, 261141297 encrypted bytes, full remote SHA-256 188ae37c773fd9255101d435161edde95e598c27268ecf0bed5a8dbff4f71e59, no local archive.
- Negative producer test: PASS, nonzero producer exit left neither committed object nor pending multipart upload.
- Vault failure/concurrent-change tests: PASS, synthetic source retained on both paths. Production dry-run preserved source Daily files.
- Package namespace test: PASS, synthetic file absent from persistent /var/backups; encrypted object read back successfully.
- Actual dpkg backup unit: PASS, Result=success and ExecMainStatus=0. APT service configuration verified; actual package upgrade/download execution intentionally not triggered.
- Gateway: same PID 1987594, active/running, NRestarts=0, authenticated health RPC and HTTP PASS. Plugin inventory: 46 loaded, zero load errors, 76 total. No claim of fresh acceptance of every plugin function.
- Hermes: same PID 1867482, active. Claude Code retained.
- ClawMem REST: status ok. Existing FindMy/startup/context-vault issues were not remediated; a transient empty FindMy lastError does not establish resolution.
- Authored OpenClaw config, Gateway unit and Hermes config hashes unchanged from cleanup baseline. Expected changes are backup scripts, backup service drop-ins, two AGENTS policy files, small health/log/manifests and authorized archive source removals.

## Production mutations and review scope

This task superseded the previous read-only audit restriction through explicit user cleanup and backup instructions. Production WAS modified: exact archived source paths removed after verification; backup scripts/three systemd drop-ins/policies changed; backup health metadata written; system manager reloaded; backup jobs/tests executed. No routes, credentials, firewall, Funnel or application package installation were changed. Sanitized evidence and source are included for independent review.

Review the streaming failure gates, RAM-only package namespace, SQLite backup consistency, source-removal gates and restored-location instructions. The exact private source-path manifests stay on the VPS and S3; GitHub contains only group-level engineering evidence. Prior update/time handoff remains independently pending; this task does not approve it.
