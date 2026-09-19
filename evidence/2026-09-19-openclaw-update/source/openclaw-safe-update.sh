#!/usr/bin/env bash
# Guarded VPS update: explicit target, verified offsite rollback, native checks.
set -Eeuo pipefail
umask 077
MODE="${1:---check}"; TARGET="${2:-latest}"; APPROVAL="${3:-}"
case "$MODE" in --dry-run) MODE=--check;; --check|--apply|--backup-only|--self-test) ;; -h|--help)
  echo 'Usage: openclaw-safe-update.sh --check|--dry-run [openclaw@VERSION|latest]'
  echo '       openclaw-safe-update.sh --apply openclaw@VERSION [--approve-bundled-doctor]'
  echo '       openclaw-safe-update.sh --backup-only|--self-test'
  echo 'Approval flag attests review and approval of native Doctor repairs for this exact run.'; exit 0;; *) exit 2;; esac
if [[ "$MODE" == --self-test ]]; then exec python3 "$(dirname "$0")/test-safe-update.py"; fi
[[ $# -le 3 && ( -z "$APPROVAL" || "$APPROVAL" == --approve-bundled-doctor ) ]] || exit 2
TARGET="${TARGET#openclaw@}"
[[ "$TARGET" == latest || "$TARGET" =~ ^[0-9]{4}\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]] || exit 2
[[ "$MODE" != --apply || "$TARGET" != latest ]] || { echo 'Explicit pinned version required for apply' >&2; exit 2; }
RUN_ROOT="${OPENCLAW_SAFE_UPDATE_RUN_ROOT:-/root/.openclaw/update-runs}"
LOCK_FILE="${OPENCLAW_SAFE_UPDATE_LOCK_FILE:-/run/lock/openclaw-safe-update.lock}"
MIN_FREE_KIB="${OPENCLAW_SAFE_UPDATE_MIN_FREE_KIB:-5242880}"
S3_STREAM="${OPENCLAW_SAFE_UPDATE_S3_STREAM:-/usr/local/bin/openclaw-s3-stream.py}"
BACKUP_PRODUCER="${OPENCLAW_SAFE_UPDATE_BACKUP_PRODUCER:-/usr/local/bin/openclaw-backup-producer.py}"
SERVICE=openclaw-gateway.service
for dep in jq openclaw sha256sum systemctl timeout flock df date; do command -v "$dep" >/dev/null || { echo "Missing dependency: $dep" >&2; exit 10; }; done
mkdir -p "$RUN_ROOT" "$(dirname "$LOCK_FILE")"; chmod 700 "$RUN_ROOT"
exec 9>"$LOCK_FILE"; flock -n 9 || { echo 'PRECHECK_FAILED: update lock held' >&2; exit 10; }
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"; RUN_DIR="$RUN_ROOT/$STAMP-$$"; mkdir -m 700 "$RUN_DIR"
BEFORE=''; BACKUP_OBJECT=''; CONFIG_SHA=''; DOCTOR=not_run; UPDATE_STARTED=false
result(){ jq -n --arg timestamp "$STAMP" --arg status "$1" --arg reason "$2" --arg before "$BEFORE" --arg target "$TARGET" --arg backup "$BACKUP_OBJECT" --arg configHash "$CONFIG_SHA" --arg doctor "$DOCTOR" --argjson started "$UPDATE_STARTED" '{timestamp:$timestamp,final_status:$status,reason:$reason,openclaw_before:$before,target:$target,backup_path:$backup,config_sha256_before:$configHash,doctor_fix_execution:$doctor,update_started:$started}' >"$RUN_DIR/result.json"; echo "$1: $2; evidence $RUN_DIR"; }
fail(){ result "$1" "$2"; exit "${3:-10}"; }
trap 'rc=$?; trap - ERR; result FAILED "unexpected_error_exit_${rc}_runtime_unverified"; exit "$rc"' ERR
trap 'trap - ERR; result INTERRUPTED runtime_unverified; exit 130' INT TERM
BEFORE="$(openclaw --version | head -1)"; VERSION="$(awk '{print $2}' <<<"$BEFORE")"
CONFIG="$(openclaw --log-level silent config file)"; CONFIG_SHA="$(sha256sum "$CONFIG" | awk '{print $1}')"
semantic_hash(){ jq -Sc '{agents,models,auth,channels,gatewayAuth:.gateway.auth}' "$CONFIG" | sha256sum | awk '{print $1}'; }
SEMANTIC_BEFORE="$(semantic_hash)"
free="$(df -Pk /opt | awk 'NR==2 {print $4}')"; (( free >= MIN_FREE_KIB )) || fail PRECHECK_FAILED insufficient_disk
timeout 120 openclaw --log-level silent config validate >"$RUN_DIR/config-validate.txt" 2>&1 || fail PRECHECK_FAILED invalid_config
[[ "$(systemctl --user is-active "$SERVICE" || true)" == active ]] || fail PRECHECK_FAILED gateway_not_active
timeout 120 openclaw --log-level silent health --timeout 90000 --json >"$RUN_DIR/health-before.json" 2>"$RUN_DIR/health-before.stderr" || fail PRECHECK_FAILED gateway_transport_failed
jq -e '.ok==true' "$RUN_DIR/health-before.json" >/dev/null || fail PRECHECK_FAILED gateway_unhealthy
EXPECTED_ACCOUNTS="$(jq '[.channels.telegram.accounts//{}|to_entries[]|select(.value.configured!=false)|.key]|sort' "$RUN_DIR/health-before.json")"
timeout 180 openclaw --log-level silent status --json >"$RUN_DIR/runtime-before.json" 2>"$RUN_DIR/runtime-before.stderr" || fail PRECHECK_FAILED runtime_status_failed
jq -e --arg version "$VERSION" '.collection.source=="gateway" and .runtimeVersion==$version and .gateway.reachable==true' "$RUN_DIR/runtime-before.json" >/dev/null || fail PRECHECK_FAILED runtime_cli_mismatch
timeout 120 openclaw --log-level silent update status --json >"$RUN_DIR/update-status-before.json" 2>"$RUN_DIR/update-status-before.stderr" || fail PRECHECK_FAILED update_status_failed
jq -e '.update.installKind=="package" and .update.packageManager=="npm"' "$RUN_DIR/update-status-before.json" >/dev/null || fail MANUAL_REVIEW_REQUIRED package_owner_unrecognized 20
jq -e '.activeRun==null' "$RUN_DIR/update-status-before.json" >/dev/null || fail PRECHECK_FAILED native_update_active
backup(){
  [[ -x "$S3_STREAM" && -x "$BACKUP_PRODUCER" ]] || fail PRECHECK_FAILED backup_tools_missing
  local key="openclaw/recovery/safe-update-$STAMP-$$.tar.gz.gpg"
  "$S3_STREAM" --key "$key" -- "$BACKUP_PRODUCER" >"$RUN_DIR/backup-result.json" || fail PRECHECK_FAILED backup_failed
  jq -e --arg key "$key" '.status=="PASS" and .local_archive_created==false and .object==$key and (.bytes|type=="number" and .>0) and (.sha256|type=="string" and test("^[0-9a-f]{64}$")) and .verification=="producer exit, encryption exit, full remote SHA-256 readback"' "$RUN_DIR/backup-result.json" >/dev/null || fail PRECHECK_FAILED backup_verification_failed
  BACKUP_OBJECT="$key"
}
if [[ "$MODE" == --backup-only ]]; then backup; result SUCCESS backup_verified; exit 0; fi
LATEST="$(jq -r '.availability.latestVersion//.update.registry.latestVersion//empty' "$RUN_DIR/update-status-before.json")"
[[ "$TARGET" != latest ]] || TARGET="$LATEST"
[[ -n "$TARGET" ]] || fail PRECHECK_FAILED registry_target_unknown
if [[ "$VERSION" == "$TARGET" ]]; then result NO_UPDATE current_version_and_health_verified; exit 0; fi
[[ "$TARGET" == "$LATEST" ]] || fail MANUAL_REVIEW_REQUIRED requested_target_not_current_release 20
if ! timeout 300 openclaw update --dry-run --tag "$TARGET" --json >"$RUN_DIR/update-dry-run.json" 2>"$RUN_DIR/update-dry-run.stderr"; then fail MANUAL_REVIEW_REQUIRED official_dry_run_refused 20; fi
if [[ "$TARGET" != 2026.9.5 && "$APPROVAL" != --approve-bundled-doctor ]]; then fail MANUAL_REVIEW_REQUIRED exact_run_doctor_approval_required 20; fi
if [[ "$MODE" == --check ]]; then result READY reviewed_target_preflight_pass; exit 0; fi
backup
[[ "$(semantic_hash)" == "$SEMANTIC_BEFORE" ]] || fail PRECHECK_FAILED config_changed_during_preflight
UPDATE_STARTED=true; DOCTOR=possible
if timeout 7200 openclaw update --tag "$TARGET" --timeout 1800 --yes --json >"$RUN_DIR/update-apply.json" 2>"$RUN_DIR/update-apply.stderr"; then native_rc=0; else native_rc=$?; fi
if jq -e '[.steps[]? | select((.command//"")|test("(^| )--fix( |$)"))]|length>0' "$RUN_DIR/update-apply.json" >/dev/null 2>&1; then DOCTOR=attempted; fi
[[ "$native_rc" == 0 ]] || fail RECOVERY_REQUIRED "native_update_failed_${native_rc}_runtime_unverified"
jq -e '.status=="ok"' "$RUN_DIR/update-apply.json" >/dev/null || fail RECOVERY_REQUIRED native_result_not_success
AFTER="$(openclaw --version | awk '{print $2}')"
[[ "$AFTER" == "$TARGET" ]] || fail RECOVERY_REQUIRED cli_version_mismatch
[[ "$(semantic_hash)" == "$SEMANTIC_BEFORE" ]] || fail MANUAL_REVIEW_REQUIRED routing_auth_or_channel_config_changed 20
timeout 600 openclaw doctor --lint --json >"$RUN_DIR/lint-after.json" 2>"$RUN_DIR/lint-after.stderr" || fail RECOVERY_REQUIRED doctor_lint_failed
jq -e '(.findings|type=="array") and all(.findings[]; .severity!="error")' "$RUN_DIR/lint-after.json" >/dev/null || fail RECOVERY_REQUIRED lint_errors
PID="$(systemctl --user show "$SERVICE" -p MainPID --value)"; [[ "$PID" =~ ^[1-9][0-9]*$ ]] || fail RECOVERY_REQUIRED gateway_not_running
for sample in 1 2 3; do
  timeout 120 openclaw --log-level silent health --timeout 90000 --json >"$RUN_DIR/health-after-$sample.json" 2>"$RUN_DIR/health-after-$sample.stderr" || fail RECOVERY_REQUIRED gateway_health_failed
  jq -e '.ok==true' "$RUN_DIR/health-after-$sample.json" >/dev/null || fail RECOVERY_REQUIRED gateway_unhealthy
  [[ "$(systemctl --user show "$SERVICE" -p MainPID --value)" == "$PID" ]] || fail RECOVERY_REQUIRED gateway_restarted_during_acceptance
  [[ "$sample" == 3 ]] || sleep 15
done
timeout 180 openclaw --log-level silent status --json >"$RUN_DIR/status-after.json" 2>"$RUN_DIR/status-after.stderr" || fail RECOVERY_REQUIRED status_failed
jq -e --arg version "$TARGET" '.collection.source=="gateway" and .runtimeVersion==$version and .gateway.reachable==true' "$RUN_DIR/status-after.json" >/dev/null || fail RECOVERY_REQUIRED gateway_version_unverified
timeout 180 openclaw --log-level silent channels status --probe --json >"$RUN_DIR/channels-after.json" 2>"$RUN_DIR/channels-after.stderr" || fail RECOVERY_REQUIRED channel_probe_failed
jq -e --argjson expected "$EXPECTED_ACCOUNTS" '(.statusIssues//[]|length)==0 and ([.channelAccounts.telegram[]?|select(.enabled!=false)|.accountId]|sort)==$expected and all(.channelAccounts.telegram[]?; .enabled==false or (.connected==true and .probe.ok==true and .lastError==null))' "$RUN_DIR/channels-after.json" >/dev/null || fail RECOVERY_REQUIRED channel_probe_unhealthy
result SUCCESS target_runtime_and_channels_verified
