# Restore cold-storage archives

Destination: established iDrive E2 bucket; object prefix openclaw-cold-storage/20260909. Never publish credentials or encryption material.

Each batch has an encrypted .tar.gz.gpg archive, a .key.gpg sidecar encrypted to the established offsite recovery public key, and a manifest. The random per-batch passphrase was held only in process memory. Source removal requires full S3 readback, SHA-256 equality, successful decryption and tar comparison against the source. The sealed sidecar is read back and byte-compared. The offsite private key must be available for a later restore; this run does not move or export that private key.

On a trusted recovery machine, obtain the archive, key sidecar and manifest using the established S3 credentials. Verify ciphertext SHA-256 against the manifest. Decrypt the .key.gpg sidecar with the offsite private key, pipe its contents as GPG passphrase input, and decrypt the symmetric archive. Extract the resulting gzip tar only into an empty isolated restore directory, preserving numeric ownership, ACLs and extended attributes where applicable. Review before restoring into production. Never put the passphrase in command arguments, shell history, logs or plaintext files.

The pre-update state archive is the complete original tar nested inside this encrypted transport archive. It must be restored with the matching pre-update binaries/config and SQLite state; do not perform a binary-only downgrade against migrated databases.

Local group manifests retain exact paths and object identities. No recovery claim is made for files not listed in a completed manifest.

Example on the trusted recovery machine (archive and sealed-key filenames are placeholders):

```bash
set -o pipefail
gpg --decrypt batch.tar.gz.gpg.key.gpg | gpg --batch --no-symkey-cache --pinentry-mode loopback --passphrase-fd 0 --output recovered.tar.gz --decrypt batch.tar.gz.gpg
mkdir isolated-restore
tar --acls --xattrs --numeric-owner -xzf recovered.tar.gz -C isolated-restore
```

Do not run this against production paths; verify the archive hash first and use an empty restore directory. The first gpg command requires the established offsite private key.
