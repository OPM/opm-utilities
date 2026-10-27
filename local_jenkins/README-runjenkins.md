# Run Jenkins locally

`run-jenkins-local.py` compiles and tests your local OPM working trees using
OPM's Jenkins scripts inside the CI builder Docker image.

## Build and test the full supported matrix (default)

From the workspace containing the sibling OPM repositories, run:

```sh
./opm-utilities/local_jenkins/run-all.sh
```

No arguments are needed. The launcher builds the CI image if it is missing,
reuses it on later runs, and keeps a persistent compiler cache. It checks GPU
access inside the CI image: NVIDIA tests run in `default` when NVIDIA access
works; AMD tests run in `hipify` and `rocm` when AMD access works. Otherwise,
those configurations still compile and run their CPU tests. `serial` runs CPU
tests. Both NVIDIA CDI and the NVIDIA Docker runtime are supported.

Results are saved under `.local-jenkins/runs/` in the workspace, with a summary
and separate logs/reports for each configuration. Temporary builds and the
compiler cache use `.local-jenkins/tmp/` and `.local-jenkins/ccache/` on the
workspace filesystem. The launcher continues through build/test failures and
returns a nonzero exit status if any configuration fails; Ctrl-C stops the run.

This configures, compiles, installs, and runs registered CTest targets for:

- Modules: `opm-common`, `opm-grid`, `opm-simulators`, and `opm-upscaling`.
- Configurations: `default`, `serial`, `hipify`, and `rocm`.

The toolchains still control which tests are registered. In particular, hipify
and rocm currently disable regression-test registration. GPU compatibility
also depends on the toolchains' architecture settings; see
[Test targets and GPUs](#test-targets-and-gpus).

For manual control, invoke `run-jenkins-local.py` directly. Without `--module`,
`--build-types`, or `--no-downstreams`, it selects this same four-by-four
matrix. The Python runner includes GPU-labelled tests by default; the Bash
launcher adds the appropriate device arguments or `--exclude-gpu-tests` for
each configuration automatically.

**Scope:** this is the full matrix supported by this runner, not every Jenkins
job. Jenkins also defines other configurations (including clang, debug, LTO,
and shared-library builds) and separate static-analysis/coverage jobs. Those
are not currently supported by the runner. Trigger-driven Norne runs and
reference-data updates are also outside this default run.

## Requirements and layout

Use a Linux host with Python 3.8 or newer, Git, Docker, and a running Docker
daemon. The runner itself uses only the Python standard library. Building the
image requires network access; compilation requires substantial disk space and
memory. Docker bind mounts must refer to paths accessible on the Docker host.

Keep these repositories as siblings:

```text
workspace/
├── opm-common/
├── opm-grid/
├── opm-simulators/
├── opm-upscaling/
├── opm-tests/
└── opm-utilities/
    ├── local_jenkins/
    │   ├── run-all.sh
    │   ├── run-jenkins-local.py
    │   ├── README-runjenkins.md
    │   └── tests/
    └── opm-ci-builder/
```

Only the selected module, its upstreams, and enabled downstreams are required.
For example, `--module opm-common --no-downstreams` needs only `opm-common`,
while `--module opm-simulators` also needs `opm-common` and `opm-grid`.
Inputs are checked before image building or snapshot preparation. `opm-tests`
supplies the regression-test input and reference data and must be a standalone
checkout (a Git worktree has metadata paths that cannot be copied into the
container). The workspace defaults to the directory containing `opm-utilities`;
use `--workspace DIR` to select a different layout.

## First run

From `opm-utilities/local_jenkins`, build the CI image and run the full supported matrix:

```sh
python3 run-jenkins-local.py /tmp/jenkins-results --build-image
```

The output directory must be absent or empty. The image is built from
`../opm-ci-builder/Dockerfile`, with the host UID, and tagged `opm-ci-builder:local`.
This is the Jenkins build image; the images under `docker_opm_user` are intended
for end users and do not supply the same build environment.

Reuse the image for subsequent runs, selecting a new output directory:

```sh
python3 run-jenkins-local.py /tmp/jenkins-results-next
```

Use `--image TAG` to select a compatible image that is already present locally.
The runner checks the daemon and image before preparing source snapshots. It
reports image-build and daemon failures in the final summary.

## Compilation and build types

Each configuration runs the selected module's `jenkins/build.sh` in a separate
container invocation and writable build tree. The existing Jenkins workflow
configures, compiles, installs, and tests the modules with a Release build and
the image's corresponding `/toolchains/NAME.cmake` file. The container receives
`WORKSPACE=/build` and `CWD=/build`; the latter is required by the shared
helper's pre-build directory stack handling.

| Build type | Jenkins configuration |
| --- | --- |
| `default` | MPI build with the default CUDA-capable CI toolchain |
| `serial` | Serial Dune build with MPI and GPU bridge disabled |
| `hipify` | Converts CUDA to HIP using the ROCm toolchain |
| `rocm` | ROCm build using the toolchain's CPU Hypre configuration |

The runner attempts the remaining configurations after a container returns a
nonzero exit code. Missing reports are failures for every attempted
configuration and tested module. Setup errors and interruption end execution.

Select a subset or a different order by placing the output argument first:

```sh
python3 run-jenkins-local.py /tmp/serial-results --build-types serial
python3 run-jenkins-local.py /tmp/gpu-builds --build-types hipify rocm default
```

By default the main module is `opm-common`, with its downstream modules
`opm-grid`, `opm-simulators`, and `opm-upscaling` also compiled and tested.
Select another main module or disable downstream testing:

```sh
python3 run-jenkins-local.py /tmp/simulator-results --module opm-simulators
python3 run-jenkins-local.py /tmp/common-only --no-downstreams --build-types serial
```

Required upstream dependencies are still built and installed by Jenkins.
`--jobs N` controls compilation concurrency (default: CPU count capped at 16).
`--test-jobs N` controls CTest concurrency (default: 2). The CTest timeout is 400
seconds, matching the CI configuration.

For repeated local runs, preserve compiler results with `--ccache-dir`:

```sh
python3 run-jenkins-local.py /tmp/next-results --build-types serial \
    --ccache-dir "$PWD/jenkins-ccache"
```

The cache directory is created if necessary, mounted writable, and retained
independently of `--keep-data`. It is shared across configurations and later
runs. Without this option, ccache is shared within a run and deleted afterward.
The image, toolchain, compiler flags, and source contents still determine cache
hits; reusing the cache does not bypass compilation checks.

## Test targets and GPUs

All registered CTest targets run by default, including GPU-labelled targets.
The runner removes Jenkins' GPU label filter in its private source snapshot.
Use `--exclude-gpu-tests` to restore that filter:

```sh
python3 run-jenkins-local.py /tmp/cpu-tests --build-types default serial --exclude-gpu-tests
```

Toolchain feature settings still determine which tests are registered. In
particular, the current hipify and rocm toolchains disable regression-test
registration. The runner preserves those Jenkins settings.

GPU test execution requires compatible host hardware and container access.
For hosts configured with the NVIDIA container runtime:

```sh
python3 run-jenkins-local.py /tmp/nvidia-tests --build-types default --gpus all
```

For an AMD host, forward devices as appropriate for the host configuration:

```sh
python3 run-jenkins-local.py /tmp/amd-tests --build-types hipify rocm \
    --device /dev/kfd --device /dev/dri
```

Device forwarding does not install host drivers or change the toolchains' GPU
architecture settings. Compilation uses the CUDA/ROCm dependencies in the CI
image; passing compilation does not establish that GPU tests can run on a
particular host.

## Local changes and isolation

The runner copies tracked working files and non-ignored untracked files,
preserving local edits and deletions. It commits these copies to temporary
`master` branches so Jenkins can fetch them through its normal dependency
checkout workflow. Original repositories, branches, indexes, and remotes are
left untouched. Submodule snapshots are not supported.

Before committing the isolated copies, the runner adapts
`jenkins/build-opm-module.sh` to check every compile/install exit status,
including downstream install failures that the helper otherwise overlooks.
It also records CTest's exit status in `ctest-status.log`, without stopping
report conversion or subsequent downstream tests, and removes the GPU test
filter unless `--exclude-gpu-tests` is set. Snapshot commits disable Git signing
so a host signing configuration does not require interaction.
Committing these adaptations keeps the Jenkins pre-build checks clean.

The original source commit IDs and Docker commands are recorded in
`logs/console.log`. The test-data checkout is mounted read-only. Jobs that call Jenkins'
`setup-opm-tests.sh` make their own writable copy. Grid without downstreams and
upscaling do not call that helper, so the runner also supplies
`OPM_TESTS_ROOT=/opm-tests` for their tests to read inputs directly. The runner does not update reference data.

## Output and data retention

A typical result directory contains:

```text
results/
├── summary.log
└── logs/
    ├── console.log
    ├── default/default/build-opm-common/...
    ├── serial/serial/build-opm-common/...
    ├── hipify/hipify/build-opm-common/...
    └── rocm/rocm/build-opm-common/...
```

The repeated configuration name reflects the outer isolated workspace and the
inner Jenkins build directory. Downstream reports use the same layout.

Retained artifacts include `.log`, `.PRT`, and `.DBG` logs, JUnit and raw CTest
XML reports, `CMakeCache.txt`, and `CTestCostData.txt`. Source snapshots, installed
binaries, ccache, copied test inputs, and simulation data are deleted by default.
Without `--keep-data`, each completed configuration's logs are collected and
its build tree is deleted before starting the next configuration. This limits
peak disk usage to one configuration plus the source snapshots and shared
ccache. Setup failures and interruption also collect logs before cleanup.
Logs shipped in the `opm-tests` input/reference tree are excluded: they describe
old reference runs, not this run, and would pollute warning comparisons.

Add `--keep-data` to retain everything under `results/work/`:

```sh
python3 run-jenkins-local.py /tmp/inspect-results --keep-data --build-types serial
```

Temporary work normally uses the system temporary directory. Check `df -h /tmp`:
on hosts where `/tmp` is a RAM-backed filesystem, build and regression data can
exhaust memory. Set `TMPDIR` to a directory on a sufficiently large disk, for
example:

```sh
mkdir -p "$PWD/jenkins-tmp"
TMPDIR="$PWD/jenkins-tmp" python3 run-jenkins-local.py /tmp/results --build-types serial
```

Reserve space for the largest selected build tree and its copy of `opm-tests`,
plus source snapshots and ccache. With `--keep-data`, reserve space for every
selected build tree.

## Failures, warnings, and exit codes

`summary.log` and the final terminal output list container/build failures,
failed tests, malformed, empty or missing reports, and new warning messages.
It also lists test counts, failures, and skips per module/configuration (without
counting Jenkins' aggregate report twice). Nonzero CTest exit statuses fail the
run even when the XML reports appear to pass. Both JUnit and raw CTest reports
are inspected: Jenkins can return zero despite a CTest failure. Intentionally
disabled tests and CTest skip-return-code/skip-regex tests count as skipped; tests that could not run due to an error still fail the
run. A test can appear in both report formats in the failure list.

Without a baseline, all detected warnings are listed. Compare with a previous
run to report only warning messages absent from its logs:

```sh
python3 run-jenkins-local.py /tmp/next-results \
    --baseline /tmp/jenkins-results --fail-on-new-warnings
```

Use the same build types and module selection for a useful comparison. Warnings
are deduplicated by message, with ANSI escapes, container build-root prefixes,
and source line/column numbers removed. Doxygen `Warnings.log` entries also
count without the word "warning". This is diagnostic text comparison rather
than Jenkins warning-plugin fingerprinting. The baseline directory should be a
complete previous runner output containing `logs/`.

| Exit code | Meaning |
| --- | --- |
| `0` | No detected failures; warnings alone are allowed by default |
| `1` | Execution/report failure, or new warnings with `--fail-on-new-warnings` |
| `2` | Invalid command-line arguments |
| `130` | Interrupted with Ctrl-C |

After Ctrl-C the runner stops its container before collecting logs and removing
temporary work. Unexpected setup errors are included in the summary. If Docker
is unavailable, inspect `logs/console.log` for the daemon error.

## Code structure and development checks

The implementation separates argument parsing (`parse_arguments`), snapshot
preparation (`snapshot`, `adapt_jenkins_helper`, `prepare_sources`), Docker setup
and command construction (`ensure_image`, `docker_command`), execution and
cleanup (`run_builds`, `execute`), and diagnostics (`collect_logs`,
`inspect_reports`, `validate_reports`, `warnings_in`, `write_summary`).
`RunState` tracks attempted configurations and failures across exceptions.
`main` coordinates those stages.

Run the host-side tests from `opm-utilities/local_jenkins`:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

These tests use temporary Git repositories and simulated Docker results.
Launcher tests also check CPU/NVIDIA/AMD routing, image reuse/building,
continuation after failures, and interruption. They
also execute the snapshotted Jenkins build function with a deliberately failing
compiler command and a CTest infrastructure failure followed by successful
report conversion. They do not establish that OPM compiles in a real CI image;
that requires running the script with a working Docker daemon.

An opt-in Docker integration test runs the actual Jenkins jobs against tiny
C++ projects in all four module slots. It checks a passing downstream build, each module as the main job,
then an uncommitted edit that fails a test, downstream continuation, report
collection, and temporary-data cleanup:

```sh
OPM_JENKINS_TEST_IMAGE=opm-ci-builder:local python3 -m unittest discover \
    -s tests -p test_run_jenkins_local_docker.py -v
```

The image must already exist and Docker must be accessible. This smoke test
checks orchestration, not compilation of the OPM sources. Its last full runner
transcript is saved as `opm-jenkins-docker-smoke.log` in the system temporary
directory. Without the environment
variable this test is skipped during ordinary test discovery.

Black is a development dependency, not a runtime dependency. Format and check
the runner and its tests using an environment with Black installed:

```sh
python3 -m black run-jenkins-local.py tests/test_*.py
python3 -m black --check run-jenkins-local.py tests/test_*.py
```

Use `python3 run-jenkins-local.py --help` for the complete option list.
