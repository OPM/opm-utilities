# Running OPM Flow in Docker with GPU support
In this section we describe how to run OPM Flow with GPU support. 

We currently support NVIDIA (CUDA) and AMD (HIP) GPUs. You will need to have Docker installed (Podman and Singularity/Apptainer should also work).

## NVIDIA (CUDA)

### Prerequisities 
In order to run this, you will need a working NVIDIA setup on your computer, including the NVIDIA drivers and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). 

Remember to have the NVIDIA Container Toolkit configured after installation, that is, you should have run

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Running
First you should clone the [opm-data](https://github.com/opm/opm-data) repository:

```bash
git clone https://github.com/opm/opm-data
cd opm-data
```

Then create a JSON file describing the linear solver on the GPU

```JSON
{
    "solver": "gpubicgstab",
    "preconditioner": {
        "type": "GPUDILU"
    }
}
```

name the JSON file `solver.json`.

Assuming you are now in the `opm-data` directory with the newly created `solver.json` file, you can run OPM Flow with GPU support through Docker as

```bash
docker run -it --init --rm -w $(pwd) -v $(pwd):$(pwd) -u $(id -u):$(id -g) \
    --gpus all \
    openporousmedia/opmreleases:24.10_nvidia \
    --linear-solver=solver.json \
    norne/NORNE_ATW2013.DATA \
    --output-dir=output \
    --matrix-add-well-contributions=true
```

We note that `norne/NORNE_ATW2013.DATA` can be replaced by any other `.DATA` DECK file.

### Using as a development image
In principle, it should be possible to use the image as a development container. Below we describe the most basic workflow that can compile OPM Flow using said container, though we are sure there are more sophisticated workflows available using extensions to VS Code, say. It is also possible to modify the Dockerfile itself, though that is not really a smooth workflow if one wishes to recompile often. 

Create the bash script `build_opm_devtainer.sh` containing

```bash
#!/bin/bash
set -e

git clone https://github.com/opm/opm-common 
git clone https://github.com/opm/opm-grid 
git clone https://github.com/opm/opm-simulators 
git clone https://github.com/opm/opm-upscaling 
git clone https://github.com/opm/opm-utilities 
cp opm-utilities/opm-super/CMakeLists.txt ./ 
mkdir -p build && cd build 
cmake \
    -DUSE_OPENCL=OFF \
    -DUSE_GPU_BRIDGE=OFF \
    ..
make -j10 flow #NOTE: Adjust number of procs as needed. OPM uses a lot of memory compiling per proc (O(2GB))
```

then run

```bash
docker run --rm -it --init --entrypoint bash \
    -v $(pwd):$(pwd) -u $(id -u):$(id -g) -w $(pwd) \
     openporousmedia/opmreleases:2024.10_nvidia \
    build_opm_devtainer.sh
```

You will then get a compiled version of OPM Flow on your local filesystem (in `$(pwd)/build/opm-simulators/bin/flow`) that you can run through the Docker image by 

```bash
docker run --rm -it --init --gpus all \
    --entrypoint $(pwd)/build/opm-simulators/bin/flow \
    -v $(pwd):$(pwd) -u $(id -u):$(id -g) -w $(pwd) \
    openporousmedia/opmreleases:2024.10_nvidia \
    --linear-solver=solver.json \
    --output-dir=output \
    --matrix-add-well-contributions=true \
    norne/NORNE_ATW2013.DATA
```

Where one assumes that `norne/NORNE_ATW2013.DATA` is accessible from the current directory (from [opm-data](https://github.com/opm/opm-data)) and `solver.json` is the file above, that is, it should be

```json
{
    "solver": "gpubicgstab",
    "preconditioner": {
        "type": "GPUDILU"
    }
}
```
## AMD (HIP)

### Prerequisities
The AMD branch also requires a working AMD driver installed with ROCm support. A good check is to run `rocminfo` without error message.

### Running

First you should clone the [opm-data](https://github.com/opm/opm-data) repository:

```bash
git clone https://github.com/opm/opm-data
cd opm-data
```

Then create a JSON file describing the linear solver on the GPU

```JSON
{
    "solver": "gpubicgstab",
    "preconditioner": {
        "type": "GPUDILU"
    }
}
```

name the JSON file `solver.json`.

Assuming you are now in the `opm-data` directory with the newly created `solver.json` file, you can run OPM Flow with GPU support through Docker as

```bash
docker run -it --init --rm -w $(pwd) -v $(pwd):$(pwd) -u $(id -u):$(id -g) \
    -v /etc/group:/etc/group:ro \
    --device /dev/dri \
    --device /dev/kfd \
    --group-add video \
    --group-add render \
    --security-opt seccomp=unconfined \
    openporousmedia/opmreleases:2024.10_amd \
    --linear-solver=solver.json \
    norne/NORNE_ATW2013.DATA \
    --output-dir=output \
    --matrix-add-well-contributions=true
```

We note that `norne/NORNE_ATW2013.DATA` can be replaced by any other `.DATA` DECK file.

#### Group render not found
If Docker complains about the `render` group not exisiting, try to replace `render` by its group number. To get the group number, you can do 

```bash
getent group render | cut -d: -f3
```

So one could then run it as 

```bash
docker run -it --init --rm -w $(pwd) -v $(pwd):$(pwd) -u $(id -u):$(id -g) \
    -v /etc/group:/etc/group:ro \
    --device /dev/dri \
    --device /dev/kfd \
    --group-add video \
    --group-add $(getent group render | cut -d: -f3) \
    --security-opt seccomp=unconfined \
    openporousmedia/opmreleases:2024.10_amd \
    --linear-solver=solver.json \
    norne/NORNE_ATW2013.DATA \
    --output-dir=output \
    --matrix-add-well-contributions=true
```

#### Other issues
It is wise to first validate that `rocminfo` can be run from the Dockerimage:

```bash
docker run -it --init --rm -w $(pwd) -v $(pwd):$(pwd) -u $(id -u):$(id -g) \
    -v /etc/group:/etc/group:ro \
    --device /dev/dri \
    --device /dev/kfd \
    --group-add video \
    --group-add render \
    --security-opt seccomp=unconfined \
    --entrypoint rocminfo \
    openporousmedia/opmreleases:2024.10_amd
```

This is a program indepdent of OPM Flow, and will tell you if the container gets proper access to the GPU.


### Using as a development image
In principle, it should be possible to use the image as a development container. Below we describe the most basic workflow that can compile OPM Flow using said container, though we are sure there are more sophisticated workflows available using extensions to VS Code, say. It is also possible to modify the Dockerfile itself, though that is not really a smooth workflow if one wishes to recompile often. 

Create the bash script `build_opm_devtainer.sh` containing

```bash
 #!/bin/bash
set -e

git clone https://github.com/opm/opm-common 
git clone https://github.com/opm/opm-grid 
git clone https://github.com/opm/opm-simulators 
git clone https://github.com/opm/opm-upscaling 
git clone https://github.com/opm/opm-utilities 
cp opm-utilities/opm-super/CMakeLists.txt ./ 
mkdir -p build && cd build 
cmake \
        -DUSE_OPENCL=OFF \
        -DUSE_BDA_BRIDGE=OFF \
        -DUSE_GPU_BRIDGE=OFF \
        -DCONVERT_CUDA_TO_HIP=ON \
        -DCMAKE_HIP_PLATFORM=amd \
        -DUSE_HIP=1 \
        -DCMAKE_PREFIX_PATH="/opt/rocm/" \
        -DCMAKE_HIP_ARCHITECTURES="gfx1100,gfx942,gfx90a,gfx908,gfx906,gfx1101" \
        ..
make -j10 flow #NOTE: Adjust number of procs as needed. OPM uses a lot of memory compiling per proc (O(2GB))
```

then run

```bash
docker run --rm -it --init --entrypoint bash \
    -v $(pwd):$(pwd) -u $(id -u):$(id -g) -w $(pwd) \
     openporousmedia/opmreleases:2024.10_amd \
    build_opm_devtainer.sh
```

You will then get a compiled version of OPM Flow on your local filesystem (in `$(pwd)/build/opm-simulators/bin/flow`) that you can run through the Docker image by (remember to adjust the group settings as described in the [Group render not found](#group-render-not-found) section). 

```bash
docker run --rm -it --init \
    --entrypoint $(pwd)/build/opm-simulators/bin/flow \
    -v $(pwd):$(pwd) -u $(id -u):$(id -g) -w $(pwd) \
    -v /etc/group:/etc/group:ro \
    --device /dev/dri \
    --device /dev/kfd \
    --group-add video \
    --group-add render \
    --security-opt seccomp=unconfined \
    openporousmedia/opmreleases:2024.10_amd \
    --linear-solver=solver.json \
    --output-dir=output \
    --matrix-add-well-contributions=true \
    norne/NORNE_ATW2013.DATA
```

Where one assumes that `norne/NORNE_ATW2013.DATA` is accessible from the current directory (from [opm-data](https://github.com/opm/opm-data)) and `solver.json` is the file above, that is, it should be

```json
{
    "solver": "gpubicgstab",
    "preconditioner": {
        "type": "GPUDILU"
    }
}
```