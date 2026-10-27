"""Opt-in integration tests using real Docker, Git, CMake, C++, and CTest.

Set OPM_JENKINS_TEST_IMAGE to a local CI builder image to enable these tests.
Small C++ fixture projects exercise the actual Jenkins scripts, not OPM physics.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

LOCAL_JENKINS = Path(__file__).resolve().parents[1]
WORKSPACE = LOCAL_JENKINS.parent.parent
IMAGE = os.environ.get("OPM_JENKINS_TEST_IMAGE")
MODULES = ("opm-common", "opm-grid", "opm-simulators", "opm-upscaling")


@unittest.skipUnless(IMAGE, "set OPM_JENKINS_TEST_IMAGE for Docker integration tests")
class DockerRunnerTests(unittest.TestCase):
    def test_compile_test_dirty_sources_downstreams_and_cleanup(self):
        # Use workspace disk rather than /tmp, which may be a small tmpfs.
        with tempfile.TemporaryDirectory(
            prefix="jenkins-smoke-", dir=LOCAL_JENKINS
        ) as tmp:
            root = Path(tmp)
            for module in MODULES:
                repo = root / module
                shutil.copytree(WORKSPACE / module / "jenkins", repo / "jenkins")
                # Keep the Jenkins job/helper but use a tiny C++ project with
                # no OPM-specific generators, tests or dependencies.
                (repo / "jenkins/pre-build.sh").unlink(missing_ok=True)
                (repo / "CMakeLists.txt").write_text(
                    "cmake_minimum_required(VERSION 3.16)\n"
                    f"project({module} LANGUAGES CXX)\n"
                    "include(CTest)\n"
                    'if(BUILD_TESTING AND NOT IS_DIRECTORY "${OPM_TESTS_ROOT}")\n'
                    '  message(FATAL_ERROR "Test input directory missing")\n'
                    "endif()\n"
                    "add_executable(smoke main.cpp)\n"
                    "add_test(NAME local-smoke COMMAND smoke)\n"
                    "add_test(NAME gpu-smoke COMMAND smoke)\n"
                    "set_tests_properties(gpu-smoke PROPERTIES LABELS gpu_cuda)\n"
                    "add_test(NAME disabled-smoke COMMAND smoke)\n"
                    "set_tests_properties(disabled-smoke PROPERTIES DISABLED TRUE)\n"
                    "install(TARGETS smoke DESTINATION bin)\n"
                )
                (repo / "main.cpp").write_text("int main() { return 0; }\n")
                self.git(repo, "init", "-q")
                self.git(repo, "add", ".")
                self.git(
                    repo,
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@localhost",
                    "-c",
                    "commit.gpgsign=false",
                    "commit",
                    "-qm",
                    "fixture",
                )
            (root / "opm-tests").mkdir()
            # setup-opm-tests.sh reports a Git revision, like the real checkout.
            self.git(root / "opm-tests", "init", "-q")
            passed = root / "passed"
            result = self.run_runner(root, passed)
            self.assertEqual(result.returncode, 0, result.stdout[-12000:])
            for module in MODULES:
                report = (
                    passed / "logs/serial/serial" / f"build-{module}/testoutput.xml"
                )
                cases = list(ET.parse(report).iter("testcase"))
                self.assertEqual(len(cases), 3)
                self.assertEqual(
                    sum(case.find("skipped") is not None for case in cases), 1
                )
                self.assertIsNone(cases[0].find("failure"))
            self.assertEqual(list((root / "tmp").iterdir()), [])
            self.assertFalse((passed / "work").exists())
            self.assertFalse(list(passed.rglob("smoke")))
            # Each other entrypoint bootstraps opm-common before sourcing the
            # helper, and installs upstreams without requiring their reports.
            for module in MODULES[1:]:
                with self.subTest(main_module=module):
                    output = root / module.replace("opm-", "main-")
                    result = self.run_runner(
                        root,
                        output,
                        "--module",
                        module,
                        "--no-downstreams",
                        "--exclude-gpu-tests",
                    )
                    self.assertEqual(result.returncode, 0, result.stdout[-12000:])
                    report = (
                        output / "logs/serial/serial" / f"build-{module}/testoutput.xml"
                    )
                    self.assertEqual(
                        {
                            case.get("name")
                            for case in ET.parse(report).iter("testcase")
                        },
                        {"local-smoke", "disabled-smoke"},
                    )
            # Uncommitted local edits must reach the container. A failed CTest
            # must fail the CLI, while the later downstream module still runs.
            (root / "opm-grid/main.cpp").write_text("int main() { return 1; }\n")
            failed = root / "failed"
            result = self.run_runner(root, failed)
            self.assertEqual(result.returncode, 1, result.stdout[-12000:])
            self.assertIn("local-smoke", (failed / "summary.log").read_text())
            self.assertTrue(
                (
                    failed / "logs/serial/serial/build-opm-upscaling/testoutput.xml"
                ).is_file()
            )
            self.assertEqual(list((root / "tmp").iterdir()), [])
            self.assertEqual(
                self.git(root / "opm-grid", "diff", "--name-only").strip(), "main.cpp"
            )

    @staticmethod
    def git(repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True)

    @staticmethod
    def run_runner(root, output, *extra):
        import sys

        temporary = root / "tmp"
        temporary.mkdir(exist_ok=True)
        result = subprocess.run(
            [
                sys.executable,
                str(LOCAL_JENKINS / "run-jenkins-local.py"),
                str(output),
                "--workspace",
                str(root),
                "--image",
                IMAGE,
                "--build-types",
                "serial",
                "--jobs",
                "2",
                *extra,
            ],
            env={**os.environ, "TMPDIR": str(temporary)},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,
        )
        # Save the full transcript outside TemporaryDirectory for diagnosis.
        (Path(tempfile.gettempdir()) / "opm-jenkins-docker-smoke.log").write_text(
            result.stdout
        )
        return result


if __name__ == "__main__":
    unittest.main()
