# Installed OpenClaw 2026.9.3 updater Doctor path

Runtime version observed read-only: `OpenClaw 2026.9.3 (1391f7c)`.

The installed policy module is:

`/opt/openclaw-2026.9.3/lib/node_modules/openclaw/dist/update-runner-doctor-rybIfBbK.mjs`

SHA-256: `f98d104f1597fd0453df359ba9b19d80a437180fb15d09874065e130862956d0`

Relevant installed lines 10-17 make `fix: true` the policy for a target at or above `2026.4.25-beta.1` when external service repair is used, and also when Gateway service repair is allowed:

```javascript
function resolveUpdateDoctorExecutionPolicy(params) {
	if (params.allowGatewayServiceRepair) return { fix: true };
	const support = compareSemverStrings(params.targetVersion, EXTERNAL_SERVICE_REPAIR_POLICY_MIN_VERSION);
	if (support !== null && support >= 0) return {
		fix: true,
		serviceRepairPolicy: "external"
	};
	return { fix: false };
}
```

The installed package-update command imports that policy at line 29 of:

`/opt/openclaw-2026.9.3/lib/node_modules/openclaw/dist/update-command-git-8rP9G_EM.mjs`

At lines 1684-1694 it resolves the policy for the candidate and conditionally appends `--fix` to the Doctor command:

```javascript
const doctorPolicy = resolveUpdateDoctorExecutionPolicy({
	targetVersion: candidateHostVersion,
	allowGatewayServiceRepair: false
});
const doctorArgv = [
	params.nodeRunner ?? resolveNodeRunner(),
	entryPath,
	"doctor",
	"--non-interactive",
	...doctorPolicy.fix ? ["--fix"] : []
];
```

For candidate `2026.9.4`, the comparison is above the policy threshold, so the installed code may construct `doctor --non-interactive --fix`. This is source-location evidence only; no update or Doctor command was executed during this remediation.
