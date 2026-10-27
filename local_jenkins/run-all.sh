#!/usr/bin/env bash
# Run every supported module/configuration, using GPUs accessible to Docker.
set -euo pipefail

if (( $# )); then
    echo "Usage: $0" >&2
    exit 2
fi

runner_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
workspace_dir=$(cd -- "$runner_dir/../.." && pwd)
data_dir="$workspace_dir/.local-jenkins"
image=opm-ci-builder:local

# Fail before creating a run directory when Docker itself is unavailable.
docker info >/dev/null
mkdir -p "$data_dir/tmp" "$data_dir/ccache" "$data_dir/runs"
results=$(mktemp -d "$data_dir/runs/$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
export TMPDIR="$data_dir/tmp"
echo "Results: $results"
trap 'exit 130' INT

if ! docker image inspect "$image" >/dev/null 2>&1; then
    docker build --build-arg "uid=$(id -u)" -t "$image" \
        "$workspace_dir/opm-utilities/opm-ci-builder" 2>&1 | tee "$results/image-build.log"
fi

nvidia_args=()
amd_args=()
container_user="$(id -u):$(id -g)"
# CDI supports current Docker installations; --gpus supports NVIDIA runtimes.
if gpu_info=$(docker run --rm --user "$container_user" \
    --device nvidia.com/gpu=all --entrypoint nvidia-smi "$image" -L 2>/dev/null) \
    && grep -Eq '^GPU [0-9]+' <<< "$gpu_info"; then
    nvidia_args=(--device nvidia.com/gpu=all)
elif gpu_info=$(docker run --rm --user "$container_user" \
    --gpus all --entrypoint nvidia-smi "$image" -L 2>/dev/null) \
    && grep -Eq '^GPU [0-9]+' <<< "$gpu_info"; then
    nvidia_args=(--gpus all)
fi

if gpu_info=$(docker run --rm --user "$container_user" \
    --device /dev/kfd --device /dev/dri --entrypoint /opt/rocm/bin/rocminfo \
    "$image" 2>/dev/null) \
    && grep -Eq 'Device Type:[[:space:]]+GPU' <<< "$gpu_info"; then
    amd_args=(--device /dev/kfd --device /dev/dri)
fi

if (( ${#nvidia_args[@]} )); then
    echo "NVIDIA GPU tests enabled for default."
else
    echo "No NVIDIA GPU accessible in Docker; default will run CPU tests."
fi
if (( ${#amd_args[@]} )); then
    echo "AMD GPU tests enabled for hipify and rocm."
else
    echo "No AMD GPU accessible in Docker; hipify and rocm will run CPU tests."
fi

failed=0
for configuration in default serial hipify rocm; do
    gpu_args=(--exclude-gpu-tests)
    case "$configuration" in
        default)
            if (( ${#nvidia_args[@]} )); then gpu_args=("${nvidia_args[@]}"); fi
            ;;
        hipify|rocm)
            if (( ${#amd_args[@]} )); then gpu_args=("${amd_args[@]}"); fi
            ;;
    esac
    echo "Building and testing all modules: $configuration"
    if python3 "$runner_dir/run-jenkins-local.py" "$results/$configuration" \
        --workspace "$workspace_dir" --image "$image" --module opm-common \
        --build-types "$configuration" --ccache-dir "$data_dir/ccache" \
        "${gpu_args[@]}"; then
        echo "$configuration: PASSED" >> "$results/summary.log"
    else
        status=$?
        echo "$configuration: FAILED (exit $status)" >> "$results/summary.log"
        if (( status == 130 )); then exit 130; fi
        failed=1
    fi
done

cat "$results/summary.log"
echo "Results: $results"
exit "$failed"
