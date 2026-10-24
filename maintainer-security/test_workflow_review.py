"""Synthetic offline tests. No workflows are executed."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("workflow_review", HERE / "workflow_review.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
PIN = "a" * 40
DIGEST = "b" * 64


def flags(text: str) -> set[str]:
    return {f["code"] for f in mod.review_text(".github/workflows/test.yml", text)}


class WorkflowReviewTests(unittest.TestCase):
    def test_pinned_action_and_explicit_read_permission(self):
        self.assertEqual(flags(f"on: push\npermissions:\n  contents: read\nsteps:\n  - uses: actions/checkout@{PIN}\n"), set())

    def test_mutable_action_tag(self):
        self.assertIn("UNPINNED_ACTION", flags("permissions: {}\nsteps:\n  - uses: actions/checkout@v4\n"))

    def test_mutable_reusable_workflow(self):
        self.assertIn("UNPINNED_ACTION", flags("permissions: {}\n  uses: owner/repo/.github/workflows/ci.yml@main"))

    def test_local_action_is_not_remote_pin(self):
        self.assertNotIn("UNPINNED_ACTION", flags("permissions: {}\n  - uses: ./local-action"))

    def test_container_digest_and_mutable_container(self):
        self.assertNotIn("MUTABLE_CONTAINER_REFERENCE", flags(f"permissions: {{}}\n- uses: docker://alpine@sha256:{DIGEST}"))
        self.assertIn("MUTABLE_CONTAINER_REFERENCE", flags("permissions: {}\n- uses: docker://alpine:latest"))

    def test_dynamic_action_reference(self):
        self.assertIn("DYNAMIC_ACTION_REFERENCE", flags("permissions: {}\n- uses: ${{ matrix.action }}"))

    def test_privileged_events(self):
        self.assertIn("PRIVILEGED_TRIGGER_REVIEW", flags("on:\n  pull_request_target:\npermissions: {}"))
        self.assertIn("PRIVILEGED_TRIGGER_REVIEW", flags("on: [push, workflow_run]\npermissions: {}"))

    def test_untrusted_expression(self):
        self.assertIn("UNTRUSTED_EXPRESSION_REVIEW", flags("permissions: {}\nrun: echo '${{ github.event.issue.title }}'"))

    def test_checkout_of_pr_head(self):
        self.assertIn("UNTRUSTED_CHECKOUT_REF_REVIEW", flags("permissions: {}\nref: ${{ github.event.pull_request.head.sha }}"))

    def test_unsafe_checkout_flag(self):
        self.assertIn("UNSAFE_PR_CHECKOUT_OPT_IN", flags("permissions: {}\nallow-unsafe-pr-checkout: true"))

    def test_broad_token_permissions(self):
        self.assertIn("BROAD_WRITE_ALL", flags("permissions: write-all"))

    def test_missing_explicit_permissions(self):
        self.assertIn("NO_EXPLICIT_PERMISSIONS_FOUND", flags("on: push\nsteps:\n - run: echo ok"))

    def test_commented_out_findings_are_ignored(self):
        self.assertEqual(flags("# on: pull_request_target\npermissions: {} # write-all\n# - uses: unsafe/action@v1"), set())

    def make_root(self, text: str):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        folder = root / ".github" / "workflows"
        folder.mkdir(parents=True)
        (folder / "ci.yml").write_text(text, encoding="utf-8")
        self.addCleanup(temporary.cleanup)
        return root

    def test_root_scan_read_only(self):
        root = self.make_root("on: push\npermissions: {}\n")
        result, status = mod.audit_root(root)
        self.assertEqual(status, 0)
        self.assertEqual(result["outcome"], "NO_RULE_MATCHES")
        self.assertEqual(result["workflow_count"], 1)
        self.assertEqual(len(list(root.rglob("*"))), 3)

    def test_findings_exit_one(self):
        root = self.make_root("permissions: write-all\n")
        result, status = mod.audit_root(root)
        self.assertEqual(status, 1)
        self.assertEqual(result["outcome"], "REVIEW_REQUIRED")

    def test_empty_workflow_directory_not_assessed(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / ".github" / "workflows").mkdir(parents=True)
            report, code = mod.audit_root(Path(t))
            self.assertEqual((report["outcome"], code), ("NOT_ASSESSED", 2))

    def test_reject_symlinked_workflow(self):
        root = self.make_root("permissions: {}")
        original = root / ".github" / "workflows" / "ci.yml"
        link = original.parent / "extra.yaml"
        try:
            link.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation not available")
        self.assertEqual(mod.audit_root(root)[1], 2)

    def test_reject_invalid_utf8(self):
        root = self.make_root("permissions: {}")
        (root / ".github" / "workflows" / "ci.yml").write_bytes(b"\xff\xfe")
        self.assertEqual(mod.audit_root(root)[1], 2)

    def test_reject_oversized_file(self):
        root = self.make_root("permissions: {}")
        (root / ".github" / "workflows" / "ci.yml").write_bytes(b"x" * (mod.MAX_FILE_BYTES + 1))
        self.assertEqual(mod.audit_root(root)[1], 2)

    def test_cli_json_and_exit_status(self):
        root = self.make_root("permissions: write-all")
        run = subprocess.run([sys.executable, str(HERE / "workflow_review.py"), str(root)],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn('"BROAD_WRITE_ALL"', run.stdout)
        self.assertNotIn("permissions: write-all", run.stdout)


if __name__ == "__main__":
    unittest.main()
