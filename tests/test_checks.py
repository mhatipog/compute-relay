import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_job", ROOT / "scripts/check_job.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestJob(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.p = Path(self.t.name)
        (self.p/"payload").mkdir()
        (self.p/"payload/main.py").write_text("print(1)\n")
        self.job = {"version":1, "id":"0123456789abcdef", "kind":"python-stdlib"}
    def tearDown(self):
        self.t.cleanup()
    def check(self):
        (self.p/"job.json").write_text(json.dumps(self.job))
        return mod.validate(self.p, "jobs/0123456789abcdef")
    def test_accept(self):
        self.assertEqual(self.check()["kind"], "python-stdlib")
    def test_reject_extra_context(self):
        self.job["project"] = "secret"
        with self.assertRaises(ValueError):
            self.check()
    def test_reject_wrong_branch(self):
        (self.p/"job.json").write_text(json.dumps(self.job))
        with self.assertRaises(ValueError):
            mod.validate(self.p, "jobs/ffffffffffffffff")
    def test_reject_unknown_kind(self):
        self.job["kind"] = "shell"
        with self.assertRaises(ValueError):
            self.check()
    def test_reject_source_symlink(self):
        (self.p/"payload/main.py").unlink()
        (self.p/"payload/main.py").symlink_to("/etc/passwd")
        with self.assertRaises(ValueError):
            self.check()

if __name__ == "__main__":
    unittest.main()
