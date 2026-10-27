"""Host-side tests; no Docker daemon or compiler required."""

import argparse
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import unittest
from io import StringIO
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "runner", Path(__file__).resolve().parents[1] / "run-jenkins-local.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_reports_catch_failures_despite_successful_container(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root / "testoutput.xml").write_text(
                '<testsuite><testcase name="bad"><failure/></testcase></testsuite>'
            )
            (root / "Test.xml").write_text(
                '<Site><Testing><Test Status="notrun"><Name>skipped dependency</Name></Test></Testing></Site>'
            )
            failures, reports = runner.inspect_reports(root)
            self.assertEqual(len(failures), 2)
            self.assertEqual(len(reports), 1)

    def test_only_logs_are_collected_and_warning_baseline_is_stable(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            work, logs, baseline = (
                root / name for name in ("work", "logs", "baseline")
            )
            work.mkdir()
            baseline.mkdir()
            (work / "output.UNRST").write_bytes(b"data")
            references = work / "deps/opm-tests/reference"
            references.mkdir(parents=True)
            (references / "case.PRT").write_text(
                "warning: historical reference warning"
            )
            (work / "testoutput.xml").write_text("<testsuite/>")
            (work / "build.log").write_text(
                "/build/deps/opm-common/foo.cpp:42:9: warning: old\nwarning: new\n"
            )
            (work / "Warnings.log").write_text("undocumented member\n")
            (baseline / "build.log").write_text(
                "opm-common/foo.cpp:12:1: warning: old\n"
            )
            runner.collect_logs(work, logs)
            self.assertFalse((logs / "output.UNRST").exists())
            self.assertFalse((logs / "deps/opm-tests").exists())
            self.assertTrue((logs / "testoutput.xml").exists())
            self.assertEqual(
                runner.warnings_in(logs) - runner.warnings_in(baseline),
                {"warning: new", "undocumented member"},
            )

    def test_snapshot_includes_dirty_and_untracked_files(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            source, target = root / "source", root / "target"
            source.mkdir()
            runner.git(source, "init", "-q")
            (source / "tracked").write_text("old")
            runner.git(source, "add", ".")
            (source / "tracked").write_text("dirty")
            (source / "untracked").write_text("new")
            (source / ".gitignore").write_text("ignored\n")
            (source / "ignored").write_text("binary")
            runner.snapshot(source, target, root / "output")
            self.assertEqual((target / "tracked").read_text(), "dirty")
            self.assertTrue((target / "untracked").exists())
            self.assertFalse((target / "ignored").exists())
            self.assertEqual(
                runner.git(target, "branch", "--show-current").strip(), b"master"
            )

    def test_full_runner_collects_reports_and_cleans_data(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            for module in runner.MODULES:
                repo = root / module
                repo.mkdir()
                runner.git(repo, "init", "-q")
                (repo / "source").write_text("source")
                (repo / "jenkins").mkdir()
                (repo / "jenkins/build.sh").write_text("#!/bin/bash\n")
                runner.git(repo, "add", ".")
                runner.git(
                    repo,
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@localhost",
                    "commit",
                    "-q",
                    "-m",
                    "fixture",
                )
            (root / "opm-tests").mkdir()
            seen = []
            configurations = []

            def fake_stream(command, log):
                if command[1] == "run":
                    seen.extend(command)
                    mount = next(arg for arg in command if "target=/build" in arg)
                    work = Path(mount.split("source=")[1].split(",target=")[0])
                    build_type = next(
                        arg.split("=", 1)[1]
                        for arg in command
                        if arg.startswith("BTYPES=")
                    )
                    # Completed configurations should not accumulate build or
                    # copied regression data unless --keep-data was requested.
                    if work.parent.name != "work":
                        for previous in configurations:
                            self.assertFalse((work.parent / previous).exists())
                    configurations.append(build_type)
                    cache_mount = next(
                        arg for arg in command if "target=/ccache" in arg
                    )
                    cache = Path(cache_mount.split("source=")[1].split(",target=")[0])
                    (cache / "cached-object").write_text("compiler cache fixture")
                    self.assertIn(
                        f"CMAKE_TOOLCHAIN_FILES=/toolchains/{build_type}.cmake", command
                    )
                    build = work / build_type / "build-opm-common"
                    build.mkdir(parents=True)
                    (build / "testoutput.xml").write_text(
                        '<testsuite><testcase name="bad"><failure/></testcase></testsuite>'
                    )
                    (build / "result.UNRST").write_text("large data")
                    log.write("warning: new compiler warning\n")
                return 0

            output = root / "output"
            with patch.object(runner, "stream", side_effect=fake_stream):
                status = runner.main(
                    [str(output), "--workspace", str(root), "--no-downstreams"]
                )
            self.assertEqual(status, 1)
            self.assertIn("bad", (output / "summary.log").read_text())
            self.assertIn("New warnings: 1", (output / "summary.log").read_text())
            self.assertFalse(list(output.rglob("*.UNRST")))
            self.assertFalse((output / "work").exists())
            self.assertIn("opm-ci-builder:local", seen)
            self.assertIn("TESTTHREADS=2", seen)
            self.assertIn("CWD=/build", seen)
            self.assertIn("OPM_TESTS_ROOT=/opm-tests", seen)
            self.assertEqual(configurations, list(runner.BUILD_TYPES))
            with patch.object(runner, "stream", side_effect=fake_stream):
                retained = root / "retained"
                self.assertEqual(
                    runner.main(
                        [
                            str(retained),
                            "--workspace",
                            str(root),
                            "--no-downstreams",
                            "--keep-data",
                            "--build-types",
                            "serial",
                        ]
                    ),
                    1,
                )
            self.assertTrue(list((retained / "work").rglob("*.UNRST")))

            configurations.clear()
            cache = root / "persistent-cache"
            with patch.object(runner, "stream", side_effect=fake_stream):
                self.assertEqual(
                    runner.main(
                        [
                            str(root / "cached-output"),
                            "--workspace",
                            str(root),
                            "--no-downstreams",
                            "--build-types",
                            "serial",
                            "--ccache-dir",
                            str(cache),
                        ]
                    ),
                    1,
                )
            self.assertTrue((cache / "cached-object").is_file())
            self.assertIn(f"type=bind,source={cache},target=/ccache", seen)

    def test_snapshot_runs_all_tests_and_fails_on_compile_errors(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            source = root / "source"
            (source / "jenkins").mkdir(parents=True)
            runner.git(source, "init", "-q")
            original = (
                Path(__file__).resolve().parents[3]
                / "opm-common/jenkins/build-opm-module.sh"
            )
            (source / "jenkins/build-opm-module.sh").write_text(original.read_text())
            target = root / "target"
            runner.snapshot(source, target, root / "output", all_tests=True)
            helper = target / "jenkins/build-opm-module.sh"
            text = helper.read_text()
            self.assertNotIn('-LE "gpu_.*"', text)
            self.assertIn(
                "cmake --build . --target install\n    test $? -eq 0 || exit 2", text
            )
            # Run the actual snapshotted Jenkins build function with failing
            # compiler command; its exit must propagate before running CTest.
            script = f"""BTYPES=serial
source '{helper}'
cmake() {{ if [[ $1 == --build ]]; then return 19; fi; return 0; }}
ctest() {{ echo unexpected-test-run; }}
configuration=serial
configurations[serial]=/toolchains/serial.cmake
configurations_build_type[serial]=Release
CWD=$PWD
build_module '' 1 "$PWD"
"""
            result = subprocess.run(
                ["bash", "-c", script], cwd=root, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn("unexpected-test-run", result.stdout)
            filtered = root / "filtered"
            runner.snapshot(source, filtered, root / "output", all_tests=False)
            self.assertIn(
                '-LE "gpu_.*"', (filtered / "jenkins/build-opm-module.sh").read_text()
            )

    def test_intentional_ctest_skips_are_not_failures(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            for completion in (
                "Disabled",
                "SKIP_RETURN_CODE=77",
                "SKIP_REGULAR_EXPRESSION_MATCHED",
            ):
                with self.subTest(completion=completion):
                    (root / "Test.xml").write_text(
                        '<Site><Testing><Test Status="notrun"><Name>skip</Name>'
                        '<Results><NamedMeasurement name="Completion Status">'
                        f"<Value>{completion}</Value></NamedMeasurement></Results>"
                        "</Test></Testing></Site>"
                    )
                    failures, _ = runner.inspect_reports(root)
                    self.assertFalse(failures)

    def test_empty_wrong_and_malformed_reports_fail(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            for content in ("<testsuite/>", "<unrelated/>", "<testsuite>"):
                with self.subTest(content=content):
                    (root / "testoutput.xml").write_text(content)
                    failures, _ = runner.inspect_reports(root)
                    self.assertTrue(failures)

    def test_ctest_infrastructure_error_is_not_hidden_by_passing_xml(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root / "testoutput.xml").write_text(
                '<testsuite><testcase name="passed"/></testsuite>'
            )
            (root / "ctest-status.log").write_text("16\n")
            failures, _ = runner.inspect_reports(root)
            self.assertEqual(len(failures), 1)
            self.assertIn("CTest exited with status '16'", next(iter(failures)))

    def test_required_modules_match_jenkins_dependencies(self):
        for module, expected in (
            ("opm-common", ("opm-common",)),
            ("opm-grid", ("opm-common", "opm-grid")),
            ("opm-simulators", runner.MODULES[:3]),
            ("opm-upscaling", ("opm-common", "opm-grid", "opm-upscaling")),
        ):
            args = argparse.Namespace(module=module, no_downstreams=True)
            self.assertEqual(runner.required_modules(args), expected)
            args.no_downstreams = False
            if module in ("opm-common", "opm-grid"):
                self.assertEqual(runner.required_modules(args), runner.MODULES)

    def test_ctest_status_survives_conversion_and_downstream_tests_continue(self):
        # Execute the real Jenkins helper, substituting only the external tools.
        # A CTest infrastructure error must be retained even when conversion
        # succeeds, and must not prevent the caller testing the next module.
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            helper_dir = root / "jenkins"
            helper_dir.mkdir()
            original = (
                Path(__file__).resolve().parents[3]
                / "opm-common/jenkins/build-opm-module.sh"
            )
            (helper_dir / original.name).write_text(original.read_text())
            runner.adapt_jenkins_helper(root, all_tests=True)
            converter = root / "deps/opm-common/jenkins/convert.py"
            converter.parent.mkdir(parents=True)
            converter.write_text(
                "#!/bin/sh\necho '<testsuite><testcase name=\"passed\"/></testsuite>'\n"
            )
            converter.chmod(0o755)
            script = f"""BTYPES=serial
source '{helper_dir / original.name}'
cmake() {{ return 0; }}
ctest() {{ return 16; }}
WORKSPACE='{root}'
CWD=$PWD
configuration=serial
ghprbCommentBody='with downstreams'
build_module '' 1 "$PWD"
echo continued
"""
            result = subprocess.run(
                ["bash", "-c", script], cwd=root, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("continued", result.stdout)
            self.assertEqual((root / "ctest-status.log").read_text(), "16\n")
            failures, _ = runner.inspect_reports(root)
            self.assertTrue(any("CTest exited" in failure for failure in failures))

    def test_selected_module_preflight_and_snapshot_do_not_need_unused_repos(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            source = root / "opm-common"
            (source / "jenkins").mkdir(parents=True)
            (source / "jenkins/build.sh").write_text("#!/bin/bash\n")
            runner.git(source, "init", "-q")
            runner.git(source, "add", ".")
            runner.git(
                source,
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@localhost",
                "commit",
                "-qm",
                "fixture",
            )
            (root / "opm-tests").mkdir()
            args = runner.parse_arguments(
                [str(root / "output"), "--workspace", str(root), "--no-downstreams"]
            )
            runner.validate_sources(args)
            runner.prepare_sources(args, root / "work", StringIO())
            self.assertEqual(
                {path.name for path in (root / "work/repos").iterdir()},
                {"opm-common"},
            )
            (root / "opm-tests/.git").write_text("gitdir: /host-only/metadata")
            with self.assertRaisesRegex(RuntimeError, "standalone checkout"):
                runner.validate_sources(args)
            args.no_downstreams = False
            with self.assertRaisesRegex(RuntimeError, "Missing source repository"):
                runner.validate_sources(args)

    def test_downstream_install_failure_propagates(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root / "jenkins").mkdir()
            original = (
                Path(__file__).resolve().parents[3]
                / "opm-common/jenkins/build-opm-module.sh"
            )
            helper = root / "jenkins" / original.name
            helper.write_text(original.read_text())
            runner.adapt_jenkins_helper(root, all_tests=False)
            script = f"""BTYPES=serial
source '{helper}'
init_and_build_module() {{ return 0; }}
cmake() {{ return 23; }}
WORKSPACE='{root}'
configuration=serial
downstreams=(opm-grid)
mkdir -p serial/build-opm-grid
build_downstreams opm-common
"""
            result = subprocess.run(
                ["bash", "-c", script], cwd=root, capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 2, result.stderr)

    def test_summary_counts_module_reports_once(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            logs = root / "logs"
            report = logs / "serial/serial/build-opm-common/testoutput.xml"
            report.parent.mkdir(parents=True)
            content = (
                '<testsuite><testcase name="passed"/>'
                '<testcase name="skipped"><skipped/></testcase>'
                '<testcase name="failed"><failure/></testcase></testsuite>'
            )
            report.write_text(content)
            (report.parent.parent / "testoutput.xml").write_text(content)
            args = argparse.Namespace(
                output=root,
                build_types=["serial"],
                fail_on_new_warnings=False,
                baseline=None,
            )
            runner.write_summary(args, logs, {"failure"}, set())
            summary = (root / "summary.log").read_text()
            self.assertEqual(summary.count("3 tests, 1 failed, 1 skipped"), 1)

    def test_daemon_failure_still_produces_summary(self):
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "output"
            with patch.object(runner, "validate_sources"), patch.object(
                runner, "stream", return_value=1
            ):
                self.assertEqual(runner.main([str(output)]), 1)
            self.assertIn(
                "Docker daemon is unavailable", (output / "summary.log").read_text()
            )
            self.assertTrue((output / "logs" / "console.log").exists())


if __name__ == "__main__":
    unittest.main()
