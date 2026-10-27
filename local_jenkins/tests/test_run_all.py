"""Exercise the Bash launcher's matrix and GPU routing without real builds."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

LAUNCHER = Path(__file__).resolve().parents[1] / "run-all.sh"
FAKE_COMMAND = r"""
import json
import os
from pathlib import Path
import sys

name = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["COMMAND_LOG"], "a") as log:
    log.write(json.dumps([name, *args]) + "\n")
if name == "python3":
    configuration = args[args.index("--build-types") + 1]
    output = Path(args[1])
    output.mkdir()
    (output / "summary.log").write_text("fixture report\n")
    sys.exit(int(os.environ.get("FAKE_EXIT_" + configuration, "0")))
if args[0] == "info":
    sys.exit(int(os.environ.get("FAKE_DAEMON_EXIT", "0")))
if args[:2] == ["image", "inspect"]:
    sys.exit(0 if os.environ.get("FAKE_IMAGE_EXISTS", "1") == "1" else 1)
if args[0] == "build":
    sys.exit(int(os.environ.get("FAKE_BUILD_EXIT", "0")))
if args[0] == "run":
    entrypoint = args[args.index("--entrypoint") + 1]
    if entrypoint == "nvidia-smi":
        mode = "runtime" if "--gpus" in args else "cdi"
        if os.environ.get("FAKE_NVIDIA") in (mode, "both"):
            print("GPU 0: Test GPU (UUID: GPU-test)")
            sys.exit(0)
    elif os.environ.get("FAKE_AMD") == "1":
        print("  Device Type: GPU")
        sys.exit(0)
    elif os.environ.get("FAKE_AMD") == "cpu":
        print("  Device Type: CPU")
        sys.exit(0)
sys.exit(1)
"""


class LauncherTests(unittest.TestCase):
    def run_launcher(self, **settings):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        workspace = Path(temporary.name) / "workspace with spaces"
        directory = workspace / "opm-utilities/local_jenkins"
        directory.mkdir(parents=True)
        launcher = directory / LAUNCHER.name
        shutil.copy2(LAUNCHER, launcher)
        (directory / "run-jenkins-local.py").touch()
        binaries = workspace / "bin"
        binaries.mkdir()
        for name in ("docker", "python3"):
            command = binaries / name
            command.write_text(f"#!{sys.executable}\n" + FAKE_COMMAND)
            command.chmod(0o755)
        command_log = workspace / "commands.jsonl"
        result = subprocess.run(
            ["bash", str(launcher)],
            cwd=workspace.parent,
            env={
                **os.environ,
                "PATH": str(binaries) + os.pathsep + os.environ["PATH"],
                "COMMAND_LOG": str(command_log),
                **settings,
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
        )
        commands = [json.loads(line) for line in command_log.read_text().splitlines()]
        invocations = [command for command in commands if command[0] == "python3"]
        return result, workspace, commands, invocations

    def test_cpu_runs_all_modules_and_configurations(self):
        result, workspace, _, invocations = self.run_launcher(FAKE_AMD="cpu")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            [command[command.index("--build-types") + 1] for command in invocations],
            ["default", "serial", "hipify", "rocm"],
        )
        for command in invocations:
            self.assertIn("--exclude-gpu-tests", command)
            self.assertNotIn("--no-downstreams", command)
            self.assertEqual(command[command.index("--module") + 1], "opm-common")
            self.assertEqual(command[command.index("--workspace") + 1], str(workspace))
            self.assertEqual(
                command[command.index("--ccache-dir") + 1],
                str(workspace / ".local-jenkins/ccache"),
            )
        summary = next((workspace / ".local-jenkins/runs").glob("*/summary.log"))
        self.assertEqual(summary.read_text().count("PASSED"), 4)

    def test_nvidia_cdi_enables_only_nvidia_configuration(self):
        result, _, _, invocations = self.run_launcher(FAKE_NVIDIA="cdi")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("nvidia.com/gpu=all", invocations[0])
        self.assertNotIn("--exclude-gpu-tests", invocations[0])
        for command in invocations[1:]:
            self.assertIn("--exclude-gpu-tests", command)

    def test_nvidia_runtime_fallback(self):
        result, _, _, invocations = self.run_launcher(FAKE_NVIDIA="runtime")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("--gpus", invocations[0])
        self.assertNotIn("--exclude-gpu-tests", invocations[0])

    def test_amd_gpu_enables_only_amd_configurations(self):
        result, _, _, invocations = self.run_launcher(FAKE_AMD="1")
        self.assertEqual(result.returncode, 0, result.stdout)
        for command in invocations[:2]:
            self.assertIn("--exclude-gpu-tests", command)
        for command in invocations[2:]:
            self.assertNotIn("--exclude-gpu-tests", command)
            self.assertIn("/dev/kfd", command)
            self.assertIn("/dev/dri", command)

    def test_failure_does_not_skip_later_configurations(self):
        result, _, _, invocations = self.run_launcher(FAKE_EXIT_default="1")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(len(invocations), 4)
        self.assertIn("default: FAILED", result.stdout)
        self.assertIn("rocm: PASSED", result.stdout)

    def test_interrupt_stops_the_matrix(self):
        result, _, _, invocations = self.run_launcher(FAKE_EXIT_default="130")
        self.assertEqual(result.returncode, 130, result.stdout)
        self.assertEqual(len(invocations), 1)

    def test_missing_image_is_built_once(self):
        result, _, commands, _ = self.run_launcher(FAKE_IMAGE_EXISTS="0")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            sum(command[:2] == ["docker", "build"] for command in commands), 1
        )

    def test_image_build_failure_stops_the_matrix(self):
        result, workspace, _, invocations = self.run_launcher(
            FAKE_IMAGE_EXISTS="0", FAKE_BUILD_EXIT="1"
        )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(invocations)
        self.assertTrue(
            list((workspace / ".local-jenkins/runs").glob("*/image-build.log"))
        )

    def test_missing_daemon_stops_before_running_tests(self):
        result, workspace, _, invocations = self.run_launcher(FAKE_DAEMON_EXIT="1")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(invocations)
        self.assertFalse((workspace / ".local-jenkins").exists())


if __name__ == "__main__":
    unittest.main()
