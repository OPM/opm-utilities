# This dockerfile builds the docker image for opm CI builds

ARG uid="1000"
FROM ubuntu:24.04 AS setup_stage
ARG uid

WORKDIR /tmp/opm
ADD . .

# Make sure we have updated URLs to packages etc.
RUN apt-get update -y

# Make sure we have updated packages
RUN apt-get upgrade -y

# Packages needed for add-apt-repository
RUN apt-get install -y software-properties-common wget apt-transport-https openssh-client

# Add apt-repo for CUDA
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb

# Add apt-repo for ROCM
RUN mkdir --parents --mode=0755 /etc/apt/keyrings
RUN wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | \
    gpg --dearmor | tee /etc/apt/keyrings/rocm.gpg > /dev/null
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/7.1 noble main" > /etc/apt/sources.list.d/rocm.list
RUN echo "Package: *" > /etc/apt/preferences.d/rocm-pin-600
RUN echo "Pin: release o=repo.radeon.com" >> /etc/apt/preferences.d/rocm-pin-600
RUN echo "Pin-Priority: 600" >> /etc/apt/preferences.d/rocm-pin-600
RUN echo "/opt/rocm/lib" > /etc/ld.so.conf.d/rocm.conf
RUN echo "/opt/rocm/lib64" >> /etc/ld.so.conf.d/rocm.conf

# Add apt-repo for the opm packages
RUN apt-add-repository ppa:opm/ppa

# Install system packages
RUN apt-get install -y cmake g++-14 git pkg-config ninja-build lld-20 clang-tidy-20 \
                       ccache clang++-20 clang-20 clang-tools-20 mold \
                       libomp-20-dev gfortran-14 gcovr \
                       libboost-date-time-dev libboost-filesystem-dev libboost-regex-dev \
                       libboost-test-dev libboost-thread-dev libboost-log-dev \
                       libboost-iostreams-dev libboost-python-dev libboost-numpy-dev \
                       libboost-program-options-dev doxygen graphviz gnuplot ghostscript \
                       libtrilinos-zoltan-dev libptscotch-dev libscotchmetis-dev \
                       libscotchparmetis-dev libhdf5-openmpi-dev libhdf5-serial-dev \
                       hdf5-tools mpi-default-bin cppcheck texlive-latex-extra \
                       mpi-default-dev libdune-common-dev libdune-istl-dev \
                       libdune-localfunctions-dev libdune-uggrid-dev \
                       libdune-grid-dev libdune-geometry-dev libdune-alugrid-dev \
                       libdune-fem-dev libamgcl-dev libvexcl-dev \
                       libxerces-c-dev xsdcxx libgmp-dev  \
                       ocl-icd-opencl-dev opencl-c-headers \
                       libfmt-dev libcjson-dev xml-twig-tools \
                       cuda-compiler-13.0 cuda-libraries-dev-13.0 cuda-nvtx-13.0 \
                       libpython3-dev python3-virtualenv python-is-python3 \
                       rocm rocm-hip-libraries rocm-hip-runtime rocm-language-runtime \
                       rocm-hip-runtime-dev rocm-hip-sdk

FROM setup_stage AS build_stage

# Install python packages
RUN scripts/setup_python_env.sh

# Setup system options
RUN scripts/setup_system_options.sh ${uid}

# Build serial dune
RUN scripts/build_dune.sh

# Build hypre
# Need to build from master branch to have rocm 7.0 fixes
RUN scripts/build_hypre.sh fca98afcd78a26b784dc24b0c3edb0e6140598af

# Build damaris
RUN scripts/build_damaris.sh v1.12.1

# Build AMGX
RUN scripts/build_amgx.sh v2.5.0

# Build debug libraries
RUN scripts/build_debug.sh

# Install infer
RUN scripts/install_infer.sh

# Make a copy of the toolchain dir
RUN cp /tmp/opm/toolchains / -r

# Apply system library patches
RUN scripts/patch_system.sh

# Remove build directory
RUN rm /tmp/opm -Rf

# Clean up apt cache
RUN apt clean

# Create shared directory
RUN mkdir /build
VOLUME /build

ENV WORKSPACE=/build
ENV TOOLCHAIN_DIR=/toolchains
ENV CMAKE_GENERATOR=Ninja
ENV CCACHE_DIR=/ccache
ENV VIRTUAL_ENV=/python_env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENTRYPOINT ["/build/jenkins/build.sh"]
