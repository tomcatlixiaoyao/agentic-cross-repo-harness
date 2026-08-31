from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_harness import validate  # noqa: E402
from doctor_harness import diagnose  # noqa: E402
from harness_lib import HarnessError, load_manifest  # noqa: E402
from init_harness import initialise  # noqa: E402
from scan_public import scan  # noqa: E402


def manifest_data() -> dict:
    return {
        "version": 1,
        "product": "test-product",
        "repositories": [
            {
                "id": "harness",
                "path": ".",
                "role": "control",
                "duty": "Coordinate plans and verification",
                "contracts": [],
                "verify": "python check.py",
            },
            {
                "id": "api",
                "path": "../test-api",
                "role": "provider",
                "duty": "Own API truth",
                "contracts": ["test-api-v1"],
                "verify": "python -m unittest",
            },
            {
                "id": "web",
                "path": "../test-web",
                "role": "consumer",
                "duty": "Own client snapshot",
                "contracts": ["test-api-v1"],
                "verify": "npm test",
            },
        ],
    }


class HarnessTests(unittest.TestCase):
    def write_manifest(self, directory: Path, data: dict | None = None) -> Path:
        path = directory / "manifest.json"
        path.write_text(json.dumps(data or manifest_data()), encoding="utf-8")
        return path

    def test_manifest_loads_valid_roles_and_control(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = load_manifest(self.write_manifest(root))
            self.assertEqual(manifest.control.repo_id, "harness")
            self.assertEqual(
                [repo.repo_id for repo in manifest.repositories],
                ["harness", "api", "web"],
            )

    def test_manifest_rejects_absolute_participant_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = manifest_data()
            data["repositories"][1]["path"] = "C:" + "/private/api"
            with self.assertRaises(HarnessError):
                load_manifest(self.write_manifest(root, data))

    def test_manifest_rejects_traversal_beyond_direct_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = manifest_data()
            data["repositories"][1]["path"] = "../../private/api"
            with self.assertRaises(HarnessError):
                load_manifest(self.write_manifest(root, data))

    def test_manifest_requires_exactly_one_control(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = manifest_data()
            data["repositories"][1]["role"] = "control"
            with self.assertRaises(HarnessError):
                load_manifest(self.write_manifest(root, data))

    def test_initialise_and_check_generated_harness(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_manifest(root)
            target = root / "test-harness"
            written = initialise(manifest, target)
            self.assertGreaterEqual(len(written), 10)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertEqual(
                (target / "CLAUDE.md").read_text(encoding="utf-8"), "@AGENTS.md\n"
            )
            self.assertTrue((target / ".cursor/rules/harness-control.mdc").is_file())
            self.assertTrue((target / ".github/copilot-instructions.md").is_file())
            self.assertTrue((target / "test-product.code-workspace").is_file())
            self.assertEqual(validate(target), [])

    def test_initializer_generates_only_selected_tool_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = manifest_data()
            data["agent_tools"] = ["cursor", "claude"]
            target = root / "test-harness"
            initialise(self.write_manifest(root, data), target)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / ".cursor/rules/harness-control.mdc").is_file())
            self.assertFalse((target / ".github/copilot-instructions.md").exists())
            generated_manifest = json.loads(
                (target / "repos.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(generated_manifest["agent_tools"], ["cursor", "claude"])
            self.assertEqual(validate(target), [])

    def test_auto_tools_detects_existing_convention(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "test-harness"
            (target / ".claude").mkdir(parents=True)
            initialise(self.write_manifest(root), target, tools="auto")
            generated_manifest = json.loads(
                (target / "repos.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(generated_manifest["agent_tools"], ["claude"])
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertFalse((target / ".cursor").exists())
            self.assertEqual(validate(target), [])

    def test_manifest_rejects_unknown_agent_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = manifest_data()
            data["agent_tools"] = ["unknown-agent"]
            with self.assertRaises(HarnessError):
                load_manifest(self.write_manifest(root, data))

    def test_manifest_rejects_duplicate_agent_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = manifest_data()
            data["agent_tools"] = ["cursor", "cursor"]
            with self.assertRaises(HarnessError):
                load_manifest(self.write_manifest(root, data))

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "preview-only"
            written = initialise(self.write_manifest(root), target, dry_run=True)
            self.assertGreater(len(written), 0)
            self.assertFalse(target.exists())

    def test_existing_managed_file_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_manifest(root)
            target = root / "test-harness"
            target.mkdir()
            (target / "README.md").write_text("user content", encoding="utf-8")
            with self.assertRaises(HarnessError):
                initialise(manifest, target)
            initialise(manifest, target, force=True)
            self.assertIn("test-product", (target / "README.md").read_text(encoding="utf-8"))

    def test_initializer_never_modifies_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sibling = root / "test-api"
            sibling.mkdir()
            marker = sibling / "marker.txt"
            marker.write_text("unchanged", encoding="utf-8")
            target = root / "test-harness"
            initialise(self.write_manifest(root), target)
            self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
            self.assertEqual(list(sibling.iterdir()), [marker])

    def test_checker_detects_workspace_registry_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "test-harness"
            initialise(self.write_manifest(root), target)
            workspace = target / "test-product.code-workspace"
            data = json.loads(workspace.read_text(encoding="utf-8"))
            data["folders"].pop()
            workspace.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("workspace folders do not match repos.yaml", validate(target))

    def test_path_verification_reports_missing_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "test-harness"
            initialise(self.write_manifest(root), target)
            findings = validate(target, verify_paths=True)
            self.assertTrue(
                any("registered sibling does not exist" in finding for finding in findings)
            )

    def test_checker_detects_missing_configured_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "test-harness"
            initialise(self.write_manifest(root), target)
            (target / "CLAUDE.md").unlink()
            self.assertIn("missing claude adapter: CLAUDE.md", validate(target))

    def test_checker_accepts_legacy_generated_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "test-harness"
            initialise(self.write_manifest(root), target)
            registry_path = target / "repos.yaml"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry.pop("agent_tools")
            registry_path.write_text(json.dumps(registry), encoding="utf-8")
            (target / "CLAUDE.md").unlink()
            (target / ".github/copilot-instructions.md").unlink()
            (target / "scripts/doctor_harness.py").unlink()
            self.assertEqual(validate(target), [])

    def test_doctor_reports_language_neutral_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "test-harness"
            initialise(self.write_manifest(root), target)
            failures, notes = diagnose(target)
            self.assertEqual(failures, [])
            self.assertTrue(any("language-neutral command" in note for note in notes))

    def test_public_scanner_detects_secret_like_value(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bad.env").write_text(
                "app_" + "secret=" + "abcdefghijklmnop123456", encoding="utf-8"
            )
            findings = scan(root)
            self.assertEqual(len(findings), 1)
            self.assertIn("assigned secret-like value", findings[0])


if __name__ == "__main__":
    unittest.main()
