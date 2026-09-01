from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_harness import validate  # noqa: E402
from discover_harness import discover, write_manifest  # noqa: E402
from doctor_harness import diagnose  # noqa: E402
from harness_lib import (  # noqa: E402
    ALLOWED_ROLES,
    HARNESS_VERSION,
    ID_PATTERN,
    PRODUCT_PATTERN,
    SUPPORTED_AGENT_TOOLS,
    HarnessError,
    load_manifest,
)
from harness_cli import main as harness_main  # noqa: E402
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

    def make_git_repository(
        self, directory: Path, name: str, files: dict[str, str] | None = None
    ) -> Path:
        repository = directory / name
        (repository / ".git").mkdir(parents=True)
        for relative, content in (files or {}).items():
            destination = repository / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return repository

    def test_discover_builds_loadable_manifest_with_conservative_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            api = self.make_git_repository(
                root,
                "catalog-api",
                {"pom.xml": "<project />", "mvnw": "wrapper"},
            )
            web = self.make_git_repository(
                root,
                "storefront_web",
                {
                    "package.json": json.dumps(
                        {"scripts": {"test": "vitest", "build": "vite build"}}
                    )
                },
            )
            ignored = self.make_git_repository(root, "ignore-me")
            (root / "ordinary-folder").mkdir()
            markers = {
                api: sorted(path.name for path in api.iterdir()),
                web: sorted(path.name for path in web.iterdir()),
                ignored: sorted(path.name for path in ignored.iterdir()),
            }

            payload = discover(
                root,
                "catalog-workspace",
                tools="codex,claude",
                exclude=["ignore-me"],
            )
            repositories = payload["repositories"]
            self.assertEqual(
                [(repo["id"], repo["path"]) for repo in repositories],
                [
                    ("harness", "."),
                    ("catalog-api", "../catalog-api"),
                    ("storefront-web", "../storefront_web"),
                ],
            )
            self.assertEqual(repositories[1]["verify"], "./mvnw test")
            self.assertEqual(
                repositories[2]["verify"], "npm test && npm run build"
            )
            self.assertEqual(payload["agent_tools"], ["codex", "claude"])

            output = root / "draft-manifest.json"
            write_manifest(payload, output)
            loaded = load_manifest(output)
            self.assertEqual(loaded.product, "catalog-workspace")
            for repository, before in markers.items():
                self.assertEqual(
                    sorted(path.name for path in repository.iterdir()), before
                )

    def test_discover_assigns_deterministic_unique_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_git_repository(root, "api-repo")
            worktree = root / "api_repo"
            worktree.mkdir()
            (worktree / ".git").write_text("gitdir: ../metadata", encoding="utf-8")

            payload = discover(root, "collision-example")
            self.assertEqual(
                [repo["id"] for repo in payload["repositories"]],
                ["harness", "api-repo", "api-repo-2"],
            )

    def test_discover_refuses_to_replace_output_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_git_repository(root, "api")
            payload = discover(root, "safe-output")
            output = root / "manifest.json"
            output.write_text("user content", encoding="utf-8")

            with self.assertRaises(HarnessError):
                write_manifest(payload, output)
            self.assertEqual(output.read_text(encoding="utf-8"), "user content")
            write_manifest(payload, output, force=True)
            self.assertEqual(load_manifest(output).product, "safe-output")

    def test_unified_cli_exposes_read_only_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_git_repository(root, "service", {"go.mod": "module example"})
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = harness_main(
                    ["discover", "--root", str(root), "--product", "cli-example"]
                )

            self.assertEqual(result, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["repositories"][1]["verify"], "go test ./...")
            self.assertEqual(
                sorted(path.name for path in root.iterdir()), ["service"]
            )

    def test_manifest_loads_valid_roles_and_control(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = load_manifest(self.write_manifest(root))
            self.assertEqual(manifest.control.repo_id, "harness")
            self.assertEqual(
                [repo.repo_id for repo in manifest.repositories],
                ["harness", "api", "web"],
            )

    def test_project_metadata_matches_runtime_version(self) -> None:
        metadata = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{HARNESS_VERSION}"', metadata)
        self.assertEqual(HARNESS_VERSION, "0.3.0")

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

    def test_java_api_web_example_generates_valid_harness(self) -> None:
        manifest = PROJECT_ROOT / "examples" / "java-api-web" / "manifest.json"
        loaded = load_manifest(manifest)
        self.assertEqual(loaded.product, "catalog-delivery-window")
        self.assertEqual(
            [(repo.repo_id, repo.role) for repo in loaded.repositories],
            [
                ("harness", "control"),
                ("catalog-api", "provider"),
                ("storefront-web", "consumer"),
            ],
        )
        self.assertEqual(
            loaded.repositories[1].contracts,
            loaded.repositories[2].contracts,
        )
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "catalog-change-harness"
            initialise(manifest, target)
            self.assertEqual(validate(target), [])
            registry = json.loads((target / "repos.yaml").read_text(encoding="utf-8"))
            self.assertEqual(
                registry["repositories"]["catalog-api"]["verify"],
                "./mvnw test",
            )
            self.assertEqual(
                registry["repositories"]["storefront-web"]["verify"],
                "npm test && npm run build",
            )

    def test_published_schema_matches_runtime_manifest_vocabulary(self) -> None:
        schema = json.loads(
            (PROJECT_ROOT / "schema" / "manifest.schema.json").read_text(
                encoding="utf-8"
            )
        )
        properties = schema["properties"]
        repository_properties = properties["repositories"]["items"]["properties"]

        self.assertEqual(properties["version"]["const"], 1)
        self.assertEqual(properties["product"]["pattern"], PRODUCT_PATTERN.pattern)
        self.assertEqual(repository_properties["id"]["pattern"], ID_PATTERN.pattern)
        self.assertEqual(set(repository_properties["role"]["enum"]), ALLOWED_ROLES)
        self.assertEqual(
            tuple(properties["agent_tools"]["items"]["enum"]),
            SUPPORTED_AGENT_TOOLS,
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(properties["repositories"]["items"]["additionalProperties"])

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
