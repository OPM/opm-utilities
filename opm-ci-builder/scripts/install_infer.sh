#!/bin/bash

set -e

wget https://github.com/facebook/infer/releases/download/v1.2.0/infer-linux-x86_64-v1.2.0.tar.xz
cd /
tar Jxvf /tmp/opm/infer-linux-x86_64-v1.2.0.tar.xz

update-alternatives --install /usr/bin/infer infer-1.2.0 /infer-linux-x86_64-v1.2.0/bin/infer 100
