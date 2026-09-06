import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('guard', Path(__file__).with_name('openclaw-provider-mitigation-check.py'))
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
class GuardTests(unittest.TestCase):
    def test_fail_closed_read_only_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); dist=root/'dist'; dist.mkdir()
            (root/'package.json').write_text('{"version":"2026.9.2"}')
            module=dist/'model-auth-provider-config-test.js'; life=dist/'runtime-snapshot-test.js'
            life.write_text('export const stable = true;')
            local='import {} from "./runtime-snapshot-test.js"; // reviewed local'
            original='import {} from "./runtime-snapshot-test.js"; // vulnerable upstream'
            upstream='import {} from "./runtime-snapshot-test.js"; // reviewed upstream fix fixture'
            token=lambda s: {'version':'2026.9.2','provider_sha256':hashlib.sha256(s.encode()).hexdigest(),'lifecycle_sha256':guard.digest(life)}
            policy={'approved_local':token(local),'known_unmitigated':token(original),'reviewed_upstream_fixes':[token(upstream)]}
            for source,expected,code in [(local,'PASS_LOCAL_MITIGATION',0),(original,'FAIL_MITIGATION_MISSING',1),(upstream,'PASS_UPSTREAM_FIXED_NO_LOCAL_PATCH',0),(local+'changed','REVIEW_REQUIRED_SOURCE_CHANGED',1)]:
                module.write_text(source); before=module.read_bytes();result,rc=guard.check(dist,policy)
                self.assertEqual((result['status'],rc),(expected,code)); self.assertEqual(module.read_bytes(),before)
            module.write_text(local); life.write_text('lifecycle changed'); self.assertEqual(guard.check(dist,policy)[1],1)
            module.write_text('unexpected source structure');self.assertEqual(guard.check(dist,policy)[1],1)
if __name__=='__main__':unittest.main()
