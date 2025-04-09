FROM ubuntu:24.04
ARG opm_version=master
ARG build_threads=4
ARG build_type=Release

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget gpg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir --parents --mode=0755 /etc/apt/keyrings && \
    wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | \
    gpg --dearmor >> /etc/apt/keyrings/rocm.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/6.3.3 noble main" >> /etc/apt/sources.list.d/rocm.list && \
    printf 'Package: *\nPin: release o=repo.radeon.com\nPin-Priority: 600' >> /etc/apt/preferences.d/rocm-pin-600 &&\
    cat  /etc/apt/preferences.d/rocm-pin-600 && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        cmake \
        curl \
        doxygen \
        gfortran \
        git \
        hipcc \
        libboost-all-dev \
        libdune-common-dev \
        libdune-grid-dev \
        libdune-istl-dev \
        libmetis-dev \
        libomp-dev \
        libopenblas-dev \
        libopenmpi-dev \
        libsuitesparse-dev \
        libtrilinos-zoltan-dev \
        m4 \
        python3-dev \
        rocm \
        rocm-device-libs \
        unzip \
        valgrind \
        wget &&\
        apt-get clean && rm -rf /var/lib/apt/lists/*rocm


RUN mkdir /fmt && \
    wget https://github.com/fmtlib/fmt/releases/download/10.2.1/fmt-10.2.1.zip && \
    unzip fmt-10.2.1.zip -d /fmt && \
    cd /fmt/fmt-10.2.1 && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=${build_type} &&\
    make -j${build_threads} && make install && \
    cd / && rm -rf /fmt

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
    mkdir build && cd build && \
    cmake \
        -DUSE_OPENCL=OFF \
        -DUSE_BDA_BRIDGE=OFF \
        -DUSE_GPU_BRIDGE=OFF \
        -DCONVERT_CUDA_TO_HIP=ON \
        -DCMAKE_CXX_FLAGS="-w" \
        -DCMAKE_HIP_PLATFORM=amd \
        -DUSE_HIP=1 \
        -DCMAKE_BUILD_TYPE=${build_type} \
        -DCMAKE_PREFIX_PATH="/opt/rocm/" \
        -DWITH_NATIVE=OFF \
        -DCMAKE_HIP_ARCHITECTURES="gfx1100,gfx942,gfx90a,gfx908,gfx906,gfx1101" \
        -DWITH_NDEBUG=ON \
        .. && \
    make -j${build_threads} flow &&\
    mv opm-simulators/bin/flow /usr/local/bin/flow && \
    cd /  && \
    rm -rf /sources
    
ENTRYPOINT ["/usr/local/bin/flow"]
CMD ["--help"]
RUN useradd opm
USER opm

