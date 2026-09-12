#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
SELF="${0##*/}"; RUN_ROOT="${OPENCLAW_SAFE_UPDATE_RUN_ROOT:-/root/.openclaw/update-runs}"; LOCK_FILE="${OPENCLAW_SAFE_UPDATE_LOCK_FILE:-/run/lock/openclaw-safe-update.lock}"
MIN_FREE_KIB="${OPENCLAW_SAFE_UPDATE_MIN_FREE_KIB:-5242880}"; S3_STREAM="${OPENCLAW_SAFE_UPDATE_S3_STREAM:-/usr/local/bin/openclaw-s3-stream.py}"; BACKUP_PRODUCER="${OPENCLAW_SAFE_UPDATE_BACKUP_PRODUCER:-/usr/local/bin/openclaw-backup-producer.py}"
SERVICE="openclaw-gateway.service"; MODE="${1:---check}"; TARGET="${2:-latest}"
usage(){ printf 'Usage: %s --check [target]\n       %s --backup-only\n       %s --apply [target]\n       %s --self-test\n' "$SELF" "$SELF" "$SELF" "$SELF"; }
case "$MODE" in --check|--backup-only|--apply|--self-test);; -h|--help) usage; exit 0;; *) usage >&2; exit 2;; esac
[[ $# -le 2 && "$TARGET" != *$'\n'* && "$TARGET" != *$'\r'* ]] || exit 2
for dep in bash date df flock jq openclaw python3 rg sha256sum systemctl timeout; do command -v "$dep" >/dev/null || { printf 'PRECHECK_FAILED: missing dependency %s\n' "$dep" >&2; exit 10; }; done
mkdir -p "$RUN_ROOT" "$(dirname "$LOCK_FILE")"; chmod 700 "$RUN_ROOT"; exec 9>"$LOCK_FILE"
flock -n 9 || { printf 'PRECHECK_FAILED: another update owns %s\n' "$LOCK_FILE" >&2; exit 10; }
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; RUN_DIR="$RUN_ROOT/$STAMP-$$"; mkdir -m 700 "$RUN_DIR"; LOG="$RUN_DIR/result.json"
BEFORE="$(openclaw --version 2>/dev/null | head -1)"; CONFIG="$(openclaw config file 2>/dev/null)"; CONFIG_SHA="$(sha256sum "$CONFIG"|awk '{print $1}')"
BACKUP_OBJECT=""; DOCTOR_FIX=false; ROLLBACK=false
write_result(){ local state="$1" ur="${2:-not_run}" dp="${3:-not_run}" rr="${4:-not_run}" ac="${5:-not_run}"; jq -n --arg timestamp "$STAMP" --arg before "$BEFORE" --arg target "$TARGET" --arg backup "$BACKUP_OBJECT" --arg update_result "$ur" --arg doctor_pre "$dp" --arg restart "$rr" --arg acceptance "$ac" --arg final_status "$state" --arg config_sha256 "$CONFIG_SHA" --argjson doctor_fix "$DOCTOR_FIX" --argjson rollback "$ROLLBACK" '{timestamp:$timestamp,openclaw_before:$before,candidate_or_after:$target,backup_path:$backup,config_sha256_before:$config_sha256,update_result:$update_result,doctor_pre_fix:$doctor_pre,doctor_fix_executed:$doctor_fix,restart_result:$restart,acceptance_result:$acceptance,rollback_attempted:$rollback,final_status:$final_status}' >"$LOG"; printf '%s: evidence %s\n' "$state" "$RUN_DIR"; }
preflight(){ local free state kind manager; free="$(df -Pk /opt|awk 'NR==2{print $4}')"; ((free>=MIN_FREE_KIB)) || { write_result PRECHECK_FAILED insufficient_disk; return 10; }; timeout 120 openclaw --log-level silent config validate >"$RUN_DIR/config-validate.txt" 2>&1 || { write_result PRECHECK_FAILED invalid_config; return 10; }; state="$(systemctl --user is-active "$SERVICE" 2>/dev/null||true)"; [[ "$state" == active ]] || { write_result PRECHECK_FAILED gateway_not_active; return 10; }; timeout 120 openclaw --log-level silent health --timeout 90000 --json >"$RUN_DIR/health-before.json" 2>"$RUN_DIR/health-before.stderr" || { write_result PRECHECK_FAILED gateway_unhealthy; return 10; }; timeout 120 openclaw --log-level silent update status --json >"$RUN_DIR/update-status-before.json" 2>"$RUN_DIR/update-status-before.stderr" || { write_result PRECHECK_FAILED update_status_failed; return 10; }; kind="$(jq -r '.update.installKind//empty' "$RUN_DIR/update-status-before.json")"; manager="$(jq -r '.update.packageManager//empty' "$RUN_DIR/update-status-before.json")"; [[ "$kind" == package && "$manager" == npm ]] || { write_result PRECHECK_FAILED "unrecognized_install:$kind:$manager"; return 10; }; }
backup(){ local key out; [[ -x "$S3_STREAM" && -x "$BACKUP_PRODUCER" ]] || { write_result PRECHECK_FAILED backup_tools_missing; return 10; }; key="openclaw/recovery/safe-update-$STAMP.tar.gz.gpg"; out="$RUN_DIR/backup-result.json"; "$S3_STREAM" --key "$key" -- "$BACKUP_PRODUCER" >"$out"; [[ "$(jq -r .status "$out")" == PASS && "$(jq -r .local_archive_created "$out")" == false && -n "$(jq -r .sha256 "$out")" ]] || { write_result PRECHECK_FAILED backup_verification_failed; return 10; }; BACKUP_OBJECT="$(jq -r .object "$out")"; }
if [[ "$MODE" == --self-test ]]; then jq -n '{availability:{available:false},update:{installKind:"package",packageManager:"npm"}}' >"$RUN_DIR/fixture-no-update.json"; [[ "$(jq -r .availability.available "$RUN_DIR/fixture-no-update.json")" == false ]]; write_result SUCCESS self_test_pass not_run not_run simulation_only; exit 0; fi
preflight
if [[ "$MODE" == --backup-only ]]; then backup; write_result SUCCESS backup_only; exit 0; fi
available="$(jq -r '.availability.available//false' "$RUN_DIR/update-status-before.json")"; latest="$(jq -r '.availability.latestVersion//.update.registry.latestVersion//empty' "$RUN_DIR/update-status-before.json")"; [[ "$TARGET" != latest ]] || TARGET="$latest"
if [[ "$available" != true || -z "$TARGET" || "$BEFORE" == *" $TARGET "* || "$BEFORE" == *" $TARGET" ]]; then write_result NO_UPDATE no_newer_applicable_release not_run not_run current_runtime_unchanged; exit 0; fi
if ! timeout 300 openclaw update --dry-run --tag "$TARGET" --json >"$RUN_DIR/update-dry-run.json" 2>"$RUN_DIR/update-dry-run.stderr"; then
  if rg -q 'package manager owner is unknown|Update refused' "$RUN_DIR/update-dry-run.json" "$RUN_DIR/update-dry-run.stderr"; then
    write_result MANUAL_REVIEW_REQUIRED blocked_before_update:official_updater_refused not_run not_run current_runtime_unchanged
    exit 20
  fi
  write_result PRECHECK_FAILED official_dry_run_failed
  exit 10
fi
if [[ "$MODE" == --check ]]; then write_result MANUAL_REVIEW_REQUIRED "candidate:$TARGET" not_run not_run dry_run_only; exit 20; fi
backup; timeout 180 openclaw --log-level silent doctor --json >"$RUN_DIR/doctor-before.json" 2>"$RUN_DIR/doctor-before.stderr" || true
# Installed 2026.9.3 package updates unconditionally invoke Doctor --fix. Refuse before mutation.
if rg -q 'fix: true|"--fix"' /opt/openclaw-2026.9.3/lib/node_modules/openclaw/dist/update-runner-doctor-*.mjs 2>/dev/null; then write_result MANUAL_REVIEW_REQUIRED blocked_before_update:bundled_doctor_fix captured not_run current_runtime_unchanged; exit 20; fi
write_result MANUAL_REVIEW_REQUIRED blocked_before_update:updater_semantics_not_reviewed captured not_run current_runtime_unchanged; exit 20
