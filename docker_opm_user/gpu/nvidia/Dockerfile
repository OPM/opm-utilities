FROM nvidia/cuda:12.6.2-devel-ubuntu24.04
ARG opm_version=master
ARG build_threads=4
ARG build_type=Release

RUN apt-get update &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common &&\
    apt-add-repository -y ppa:opm/ppa && apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential\
    cmake\
    curl\
    libdune-common-dev\
    libdune-grid-dev\
    libdune-istl-dev\
    gfortran\
    git\
    libboost-all-dev\
    libfmt-dev\
    libmetis-dev\
    libomp-dev\
    libopenblas-dev\
    libopenmpi-dev\
    libsuitesparse-dev\
    libtrilinos-zoltan-dev\
    m4\
    python3-dev\
    rocm-cmake\
    unzip\
    valgrind\
    wget\
    doxygen &&\
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /sources; cd /sources && \
    git clone https://github.com/opm/opm-common &&\
    git clone https://github.com/opm/opm-grid &&\
    git clone https://github.com/opm/opm-simulators &&\
    git clone https://github.com/opm/opm-upscaling &&\
    git clone https://github.com/opm/opm-utilities && \
    if [ ${opm_version} != "master" ]; then \
        cd opm-common && git checkout release/${opm_version}/final && cd .. &&\
        cd opm-grid && git checkout release/${opm_version}/final && cd .. &&\
        cd opm-simulators && git checkout release/${opm_version}/final && cd .. &&\
        cd opm-upscaling && git checkout release/${opm_version}/final && cd ..;\
    fi &&\
    cp opm-utilities/opm-super/CMakeLists.txt ./ && \
    mkdir build && cd build &&\
    cmake \
        -DUSE_OPENCL=OFF \
        -DUSE_GPU_BRIDGE=OFF \
        -DCMAKE_BUILD_TYPE=${build_type} \
        -DWITH_NATIVE=OFF \
        -DWITH_NDEBUG=ON \
        ..\
    && make -j${build_threads} flow &&\
    mv opm-simulators/bin/flow /usr/local/bin/flow && \
    cd /  && \
    rm -rf /sources

ENTRYPOINT ["/usr/local/bin/flow"]
CMD ["--help"]
RUN useradd opm
USER opm

