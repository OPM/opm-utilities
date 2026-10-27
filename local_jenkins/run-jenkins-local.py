#!/usr/bin/env python3
"""Compile and test local OPM checkouts using the Jenkins Docker environment.

The host orchestrates source snapshots, container execution, and report analysis.
Compilation and CTest execution remain in the existing Jenkins shell scripts.
Only diagnostic artifacts survive unless --keep-data is requested. See
README-runjenkins.md for setup, command examples, and implementation notes.
"""

import argparse
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import List, Optional, Sequence, Set, TextIO, Tuple
import uuid
import xml.etree.ElementTree as ET

MODULES = ("opm-common", "opm-grid", "opm-simulators", "opm-upscaling")
BUILD_TYPES = ("default", "serial", "hipify", "rocm")
WARNING = re.compile(r"\bwarning\b", re.I)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
LOG_SUFFIXES = {".log", ".prt", ".dbg"}
REPORT_FILES = {"testoutput.xml", "Test.xml", "CTestCostData.txt", "CMakeCache.txt"}
EXCLUDED_LOG_DIRS = {".git", "repos", "ccache", "install", "opm-tests"}
UPSTREAMS = {
    "opm-common": (),
    "opm-grid": ("opm-common",),
    "opm-simulators": ("opm-common", "opm-grid"),
    "opm-upscaling": ("opm-common", "opm-grid"),
}
DOWNSTREAMS = {"opm-common": MODULES[1:], "opm-grid": MODULES[2:]}


@dataclass
class RunState:
    """Mutable execution results that remain available after errors or Ctrl-C."""

    failures: Set[str] = field(default_factory=set)
    attempted: List[str] = field(default_factory=list)
    interrupted: bool = False


def stream(command: Sequence[str], log: TextIO, **kwargs) -> int:
    """Tee a subprocess to the terminal and log, returning its exit status.

    Terminate the client on interruption; the caller must also stop any Docker
    container, since terminating the client does not necessarily stop its job.
    """
    log.write("$ " + shlex.join(map(str, command)) + "\n")
    log.flush()
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        **kwargs,
    ) as process:
        try:
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
            return process.wait()
        except BaseException:
            process.terminate()
            process.wait()
            raise


def git(repo: Path, *args: str) -> bytes:
    """Run Git in a repository and return raw output (including NUL filenames)."""
    return subprocess.check_output(["git", "-C", str(repo), *args])


def snapshot(
    source: Path, target: Path, excluded: Path, all_tests: bool = False
) -> None:
    """Commit an isolated copy of the current working files on a master branch.

    Include tracked edits, deletions, symlinks, and non-ignored untracked files.
    Exclude the output directory if it lives inside a source checkout. Fresh
    commits let Jenkins fetch local changes through its normal Git workflow,
    without changing the original checkout's index, branches, or remotes.
    Submodules require separate snapshot handling and are rejected explicitly.
    """
    target.mkdir(parents=True)
    names = git(source, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for name in set(names.split(b"\0")) - {b""}:
        relative = Path(os.fsdecode(name))
        src = source / relative
        if excluded == src or excluded in src.parents:
            continue
        dst = target / relative
        if src.is_symlink():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(os.readlink(src))
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif src.is_dir():
            raise RuntimeError(f"Submodules are not supported: {src}")
    adapt_jenkins_helper(target, all_tests)
    git(target, "init", "-q", "-b", "master")
    git(target, "add", "--all", "--force")
    git(
        target,
        "-c",
        "user.name=Local Jenkins",
        "-c",
        "user.email=local@localhost",
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "Local working tree snapshot",
    )


def adapt_jenkins_helper(repository: Path, all_tests: bool) -> None:
    """Adapt only the snapshot's helper, before committing it.

    Jenkins filters GPU tests and overlooks some install exit statuses. Remove
    the filter when requested and propagate every build/install failure. Keeping
    these edits in the snapshot commit also keeps Jenkins pre-build checks clean.
    """
    helper = repository / "jenkins" / "build-opm-module.sh"
    if helper.is_file():
        text = helper.read_text()
        if all_tests:
            text = text.replace(' -LE "gpu_.*"', "")
        # Preserve CTest's status without stopping later downstream tests or
        # report conversion. Jenkins otherwise loses infrastructure errors when
        # a complete-looking XML report has already been written.
        text = re.sub(
            r"(?m)^( +)(ctest .*)$",
            r"\1\2\n\1echo $? > ctest-status.log",
            text,
        )
        # Jenkins does not check the downstream install command's status.
        # Check every compile/install command in the isolated snapshot.
        text = re.sub(
            r"(?m)^( +)(cmake --build .*)$", r"\1\2\n\1test $? -eq 0 || exit 2", text
        )
        helper.write_text(text)


def collect_logs(work: Path, output: Path) -> None:
    """Whitelist logs and test reports; never copy simulator data or binaries."""
    for root, dirs, files in os.walk(work, followlinks=False):
        dirs[:] = [
            d
            for d in dirs
            if d not in EXCLUDED_LOG_DIRS and not (Path(root) / d).is_symlink()
        ]
        for name in files:
            src = Path(root) / name
            if src.is_symlink():
                continue
            if src.suffix.lower() in LOG_SUFFIXES or name in REPORT_FILES:
                dst = output / src.relative_to(work)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)


def inspect_reports(logs: Path) -> Tuple[Set[str], List[Path]]:
    """Find failed/not-run tests and malformed reports independently of Docker.

    Jenkins can return zero after CTest failures, so its process status alone
    cannot establish success. Inspect both converted JUnit and raw CTest reports.
    """
    failures = set()
    reports = list(logs.rglob("testoutput.xml"))
    for report in reports:
        try:
            tree = ET.parse(report)
            if tree.getroot().tag not in ("testsuite", "testsuites"):
                failures.add(f"Invalid JUnit root in {report.relative_to(logs)}")
            if not list(tree.iter("testcase")):
                failures.add(f"No tests recorded in {report.relative_to(logs)}")
            for case in tree.iter("testcase"):
                if case.find("failure") is not None or case.find("error") is not None:
                    failures.add(
                        f'{report.relative_to(logs)}: {case.get("name", "unnamed test")}'
                    )
        except ET.ParseError as error:
            failures.add(f"Invalid test report {report.relative_to(logs)}: {error}")
    # CTest records failures even when Jenkins fails to convert its report.
    for report in logs.rglob("Test.xml"):
        try:
            for case in ET.parse(report).iter("Test"):
                completion = case.findtext(
                    "Results/NamedMeasurement[@name='Completion Status']/Value", ""
                )
                skipped = completion == "Disabled" or completion.startswith("SKIP_")
                if case.get("Status") == "failed" or (
                    case.get("Status") == "notrun" and not skipped
                ):
                    failures.add(
                        f'{report.relative_to(logs)}: {case.findtext("Name", "unnamed test")}'
                    )
        except ET.ParseError as error:
            failures.add(f"Invalid CTest report {report.relative_to(logs)}: {error}")
    for status in logs.rglob("ctest-status.log"):
        value = status.read_text().strip()
        if value != "0":
            failures.add(
                f"{status.relative_to(logs)}: CTest exited with status {value!r}"
            )
    return failures, reports


def warnings_in(folder: Path) -> Set[str]:
    """Read normalized warning messages for comparison with a prior run.

    Doxygen Warnings.log entries count even without the word 'warning'. Source
    line/column numbers and container build roots are removed so moving a line
    does not by itself introduce a new warning. This is text comparison, not a
    reproduction of Jenkins warning-plugin fingerprints.
    """
    warnings = set()
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in LOG_SUFFIXES:
            with path.open(errors="replace") as source:
                for line in source:
                    line = ANSI.sub("", line).strip()
                    if WARNING.search(line) or (path.name == "Warnings.log" and line):
                        # Ignore build roots and diagnostic line/column changes.
                        line = re.sub(r"/build/(?:deps/)?", "", line)
                        line = re.sub(r":\d+(?::\d+)?:", ":", line)
                        warnings.add(line)
    return warnings


def positive(value: str) -> int:
    """Argparse converter for positive thread counts."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse the CLI and reject invalid output/baseline paths before writing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", type=Path, help="directory for logs and summary (must be empty)"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="parent directory of the local OPM repositories",
    )
    parser.add_argument("--module", choices=MODULES, default="opm-common")
    parser.add_argument(
        "--build-types",
        nargs="+",
        choices=BUILD_TYPES,
        default=list(BUILD_TYPES),
        help="Jenkins configurations to compile and test (default: all four)",
    )
    parser.add_argument(
        "--exclude-gpu-tests",
        action="store_true",
        help="use Jenkins GPU test exclusion instead of testing all targets",
    )
    parser.add_argument(
        "--gpus", help="Docker GPU request, for example all (NVIDIA runtime required)"
    )
    parser.add_argument(
        "--device",
        action="append",
        default=[],
        help="device to pass to Docker; repeat for /dev/kfd and /dev/dri on AMD",
    )
    parser.add_argument(
        "--image", default="opm-ci-builder:local", help="CI image to run"
    )
    parser.add_argument(
        "--build-image",
        action="store_true",
        help="build image from opm-ci-builder first",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="retain full work directory as output/work",
    )
    parser.add_argument(
        "--ccache-dir",
        type=Path,
        help="persistent compiler cache directory to reuse across runs",
    )
    parser.add_argument("--no-downstreams", action="store_true")
    parser.add_argument("--jobs", type=positive, default=min(os.cpu_count() or 1, 16))
    parser.add_argument("--test-jobs", type=positive, default=2)
    parser.add_argument(
        "--baseline", type=Path, help="previous run directory for warning comparison"
    )
    parser.add_argument("--fail-on-new-warnings", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    workspace = args.workspace.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error("output directory must be empty")
    if args.baseline and not (args.baseline / "logs").is_dir():
        parser.error("baseline must be a previous run directory containing logs/")
    if args.ccache_dir:
        args.ccache_dir = args.ccache_dir.resolve()
        if args.ccache_dir.exists() and not args.ccache_dir.is_dir():
            parser.error("--ccache-dir must be a directory")
    args.output = output
    args.workspace = workspace
    args.build_types = list(dict.fromkeys(args.build_types))
    return args


def ensure_image(args: argparse.Namespace, log: TextIO) -> None:
    """Check Docker availability and optionally build the official CI image."""
    if stream(["docker", "info"], log):
        raise RuntimeError("Docker daemon is unavailable")
    if args.build_image:
        context = args.workspace / "opm-utilities" / "opm-ci-builder"
        if stream(
            [
                "docker",
                "build",
                "--build-arg",
                f"uid={os.getuid()}",
                "-t",
                args.image,
                str(context),
            ],
            log,
        ):
            raise RuntimeError("CI image build failed")
    if stream(["docker", "image", "inspect", args.image], log):
        raise RuntimeError(
            f"Image {args.image} unavailable; use --build-image or --image"
        )


def required_modules(args: argparse.Namespace) -> Tuple[str, ...]:
    """Return the main module and the dependencies its Jenkins job fetches."""
    selected = {args.module, *UPSTREAMS[args.module]}
    if not args.no_downstreams:
        selected.update(DOWNSTREAMS.get(args.module, ()))
    return tuple(module for module in MODULES if module in selected)


def validate_sources(args: argparse.Namespace) -> None:
    """Fail before an expensive image build or snapshot if inputs are missing."""
    for module in required_modules(args):
        source = args.workspace / module
        if not source.is_dir():
            raise RuntimeError(f"Missing source repository: {source}")
        git(source, "rev-parse", "--verify", "HEAD")
        if not (source / "jenkins" / "build.sh").is_file():
            raise RuntimeError(f"Missing Jenkins entrypoint: {source}/jenkins/build.sh")
    tests = args.workspace / "opm-tests"
    if not tests.is_dir():
        raise RuntimeError(f"Missing test data directory: {tests}")
    # Jenkins copies .git as well as data; a worktree's gitfile points outside
    # the mount. Reject it instead of producing misleading failures later.
    if (tests / ".git").is_file():
        raise RuntimeError(
            "opm-tests must be a standalone checkout, not a Git worktree"
        )


def prepare_sources(args: argparse.Namespace, work: Path, log: TextIO) -> None:
    """Snapshot sibling repositories and record original commits in the log."""
    repos = work / "repos"
    for module in required_modules(args):
        source = args.workspace / module
        snapshot(
            source, repos / module, args.output, all_tests=not args.exclude_gpu_tests
        )
        log.write(
            f'{module} original HEAD: {git(source, "rev-parse", "HEAD").decode().strip()}\n'
        )
    (args.ccache_dir or work / "ccache").mkdir(parents=True, exist_ok=True)


def docker_command(
    args: argparse.Namespace, work: Path, build_type: str, container: str
) -> List[str]:
    """Assemble one Jenkins invocation with its exact toolchain and bind mounts.

    Each build type receives its own writable source/build tree. Snapshots and
    original test inputs are mounted read-only; ccache is shared across types.
    Explicit BTYPES bypasses the image's comment-based configuration selection,
    so its usual thread and test-data environment defaults are supplied here.
    """
    trigger = (
        "jenkins build this"
        + ("" if args.no_downstreams else " with downstreams")
        + " please"
    )
    command = [
        "docker",
        "run",
        "--rm",
        "--name",
        container,
        "--shm-size=2048m",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--workdir",
        "/build",
        "--entrypoint",
        "/build/jenkins/build.sh",
    ]
    if args.gpus:
        command.extend(["--gpus", args.gpus])
    for device in args.device:
        command.extend(["--device", device])
    env = {
        "WORKSPACE": "/build",
        "CWD": "/build",
        "TOOLCHAIN_DIR": "/toolchains",
        "OPM_REPO_ROOT": "/repos",
        "absolute_revisions": "1",
        "sha1": "master",
        "ghprbCommentBody": trigger,
        "BUILDTHREADS": str(args.jobs),
        "TESTTHREADS": str(args.test_jobs),
        "HOME": "/tmp",
        "BTYPES": build_type,
        "BUILD_CONFIGS": "Release",
        "CMAKE_TOOLCHAIN_FILES": f"/toolchains/{build_type}.cmake",
        "OPM_TESTS_ROOT_PREDEFINED": "/opm-tests",
        # Grid without downstreams and upscaling do not source setup-opm-tests.
        # Their main-module tests still need a valid input-data root.
        "OPM_TESTS_ROOT": "/opm-tests",
        "CTEST_TIMEOUT": "400",
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "2",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "safe.directory",
        "GIT_CONFIG_VALUE_0": "*",
    }
    for key, value in env.items():
        command.extend(["--env", f"{key}={value}"])
    for host, guest, mode in (
        (work / build_type, "/build", "rw"),
        (work / "repos", "/repos", "ro"),
        (args.ccache_dir or work / "ccache", "/ccache", "rw"),
        (args.workspace / "opm-tests", "/opm-tests", "ro"),
    ):
        if not host.is_dir():
            raise RuntimeError(f"Missing directory: {host}")
        if "," in str(host):
            raise RuntimeError(f"Docker mount paths cannot contain commas: {host}")
        command.extend(
            [
                "--mount",
                f"type=bind,source={host},target={guest}"
                + (",readonly" if mode == "ro" else ""),
            ]
        )
    return command + [args.image]


def run_builds(
    args: argparse.Namespace, work: Path, container: str, log: TextIO, state: RunState
) -> None:
    """Compile/test each selected configuration, continuing after nonzero exits."""
    for build_type in args.build_types:
        print(f"Compiling and testing Jenkins configuration: {build_type}", flush=True)
        shutil.copytree(work / "repos" / args.module, work / build_type, symlinks=True)
        command = docker_command(args, work, build_type, container)
        state.attempted.append(build_type)
        status = stream(command, log)
        if status:
            state.failures.add(
                f"{build_type}: Jenkins compilation/test container exited with status {status}"
            )
        if not args.keep_data:
            # The container has exited, so its mount can now be reclaimed.
            # Keep only one configuration's builds/test-data copies on disk.
            collect_logs(work / build_type, args.output / "logs" / build_type)
            shutil.rmtree(work / build_type)


def validate_reports(args: argparse.Namespace, logs: Path, state: RunState) -> None:
    """Require a report for every tested module in every attempted build type."""
    report_failures, reports = inspect_reports(logs)
    state.failures.update(report_failures)
    if state.attempted and not reports:
        state.failures.add("No JUnit test reports produced")
    expected = (args.module,) + (
        () if args.no_downstreams else DOWNSTREAMS.get(args.module, ())
    )
    for build_type in state.attempted:
        for module in expected:
            report = (
                logs / build_type / build_type / ("build-" + module) / "testoutput.xml"
            )
            if not report.is_file():
                state.failures.add(f"{build_type}: missing test report for {module}")


def write_summary(
    args: argparse.Namespace, logs: Path, failures: Set[str], new_warnings: Set[str]
) -> int:
    """Save and print the final diagnostics; return zero only for a passing run."""
    output = args.output
    failed = bool(failures or (args.fail_on_new_warnings and new_warnings))
    test_counts = []
    # Module reports avoid double-counting Jenkins' aggregate JUnit files.
    for report in sorted(logs.glob("*/*/build-*/testoutput.xml")):
        try:
            cases = list(ET.parse(report).iter("testcase"))
        except ET.ParseError:
            continue  # Already diagnosed by inspect_reports.
        skipped = sum(case.find("skipped") is not None for case in cases)
        unsuccessful = sum(
            case.find("failure") is not None or case.find("error") is not None
            for case in cases
        )
        test_counts.append(
            f"  {report.relative_to(logs)}: {len(cases)} tests, "
            f"{unsuccessful} failed, {skipped} skipped"
        )
    lines = [
        "Jenkins build types: " + ", ".join(args.build_types),
        f'Result: {"FAILED" if failed else "PASSED"}',
        "Test reports:",
        *(test_counts or ["  none"]),
        f"Failures: {len(failures)}",
        *("  " + item for item in sorted(failures)),
        f"New warnings: {len(new_warnings)}"
        + ("" if args.baseline else " (no baseline; all warnings reported)"),
        *("  " + item for item in sorted(new_warnings)),
        f"Logs: {logs}",
    ]
    summary = "\n".join(lines) + "\n"
    (output / "summary.log").write_text(summary)
    print(summary, end="")
    return int(failed)


def execute(args: argparse.Namespace, logs: Path, state: RunState) -> None:
    """Own the container and workspace lifecycle, preserving logs on failure.

    Collect diagnostics before deleting temporary data. When retaining data,
    use output/work instead. On Ctrl-C stop the container before reading files
    or removing its bind-mounted workspace.
    """
    container = "opm-local-" + uuid.uuid4().hex
    temporary = None
    work = None
    try:
        with (logs / "console.log").open("w", buffering=1) as log:
            validate_sources(args)
            ensure_image(args, log)
            if args.keep_data:
                work = args.output / "work"
                work.mkdir()
            else:
                temporary = tempfile.TemporaryDirectory(prefix="opm-jenkins-")
                work = Path(temporary.name)
            prepare_sources(args, work, log)
            run_builds(args, work, container, log, state)
    except KeyboardInterrupt:
        state.interrupted = True
        state.failures.add("Run interrupted")
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        state.failures.add(str(error))
    finally:
        if state.interrupted:
            subprocess.run(
                ["docker", "rm", "-f", container],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        try:
            if work:
                collect_logs(work, logs)
        except OSError as error:
            state.failures.add(f"Could not collect logs: {error}")
        finally:
            if temporary:
                temporary.cleanup()


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Coordinate CLI parsing, execution, report checks, and the final summary."""
    args = parse_arguments(argv)
    baseline = warnings_in(args.baseline.resolve() / "logs") if args.baseline else set()
    args.output.mkdir(parents=True, exist_ok=True)
    logs = args.output / "logs"
    logs.mkdir()
    state = RunState()
    execute(args, logs, state)
    validate_reports(args, logs, state)
    status = write_summary(args, logs, state.failures, warnings_in(logs) - baseline)
    return 130 if state.interrupted else status


if __name__ == "__main__":
    sys.exit(main())
