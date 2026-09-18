# Rollback and installation boundary

Current stage: staging files only. No Hermes profile or runtime file has changed. Rollback now is to leave this directory unused. The normal Hermes gateway, default profile, OpenClaw, and models remain as they were.

After Andrea explicitly approves installation: use the documented `hermes profile create cleo-candidate` path, prepare independent profile configuration and credentials without copying private memory or messaging tokens, and install candidate SOUL/USER only there. Record hashes before and after each profile-local edit; stream any required rollback copy encrypted to the established S3 destination before mutation. Do not use a local backup archive. Keep candidate gateway off until isolated tests are ready.

If behavior or reliability regresses, stop the candidate gateway/session, switch any test client back to `default`, and leave the candidate profile inert. Restore candidate-only files from the verified S3 rollback copy if another candidate iteration is approved. Do not delete the profile or change the default profile as an automatic rollback step.
