#!/usr/bin/env bash
#
# A small script to run the SPE11 cases to test two versions of OPM Flow,
# generating PNGs to compare the results. The resuls are saved in three folders
# spe11a, b, and c, with two subfolders each (FLOW1 and FLOW2). Then plopm is used
# to generate plots of the spatial maps (for spe11c the slide corresponds to the
# middle part) and for performance quantities msumlins and msumnewt, in addition to
# the total (theoretical) mass. Takes as arguments the path to the first flow
# executable (default "flow"), the second path (default "/path/to/coming/release"),
# and number of cores to run OPM Flow (default "8"). For macOS, this requires to
# install bash (e.g., brew install bash).
#
# Example: Test the comming release located in /Users/build/opm-simulators/bin/flow
# with the current release using 8 CPUs.
#
#    bash spe11-compare-opm-release.sh /Users/build/opm-simulators/bin/flow flow 8
#

set -e

FLOW1=${1:-flow}
FLOW2=${2:-/path/to/coming/release}
CPUS=${3:-8}

if [ ! -d venv ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip setuptools wheel
  pip install git+https://github.com/cssr-tools/plopm.git
  pip install git+https://github.com/OPM/pyopmspe11.git
else
  source venv/bin/activate
fi
if ! command -v pyopmspe11 >/dev/null 2>&1; then
  pip install git+https://github.com/OPM/pyopmspe11.git
fi
if ! command -v plopm >/dev/null 2>&1; then
  pip install git+https://github.com/cssr-tools/plopm.git
fi

declare -A flows versions total_mass units slide format cases mpiruns 
flows[flow1]=$FLOW1
flows[flow2]=$FLOW2
if grep -q ":" <<< $FLOW1
then
  versions[flow1]="$(docker run $FLOW1 flow --version | cut -c6-)"
else
  versions[flow1]="$($FLOW1 --version | cut -c6-)"
fi
if grep -q ":" <<< $FLOW2
then
  versions[flow2]="docker run $FLOW2 flow --version | cut -c6-)"
else
  versions[flow2]="$($FLOW2 --version | cut -c6-)"
fi
cases[a]=r3_cp_1cmish_capmax2500Pa
cases[b]=r2_cp_10mish
cases[c]=r2_cp_50m-50m-8mish
total_mass[a]=4.59e-3
total_mass[b]=8.2782e7
total_mass[c]=1.1826e11
mpiruns[a]=32
mpiruns[b]=32
mpiruns[c]=64
units[a]=h
units[b]=y
units[c]=y
slide[a]=1
slide[b]=1
slide[c]=13
format[tcpu]=.1e
format[msumlins]=.0f
format[msumnewt]=.0f

for x in a b c; do
  if [ -d spe11$x ]; then
    rm -rf spe11$x
  fi
  mkdir spe11$x && cd spe11$x
  n=1
  for flow in flow1 flow2; do
    curl -L -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/benchmark/spe11$x/${cases[$x]}.toml
    sed -i.bak "s|-np ${mpiruns[$x]}|-np $CPUS|g" ${cases[$x]}.toml
    sed -i.bak "s|flow --|${flows[$flow]} --|g" ${cases[$x]}.toml
    rm -f ${cases[$x]}.toml.bak
    pyopmspe11 -i ${cases[$x]}.toml -o FLOW$n -f 0
    n=$((n + 1))
  done
  # Spatial maps for CO2 mass fraction (modify this for a different quantity, i.e., pressure)
  plopm -i 'FLOW1/FLOW1 FLOW2/FLOW2' -subfigs 2,1 -t "Flow ${versions[flow1]}  Flow ${versions[flow2]}" -cbsfax 0.25,0.93,0.5,0.02 -delax 1 -v xco2l -clabel 'CO$_2$ mass fraction (liquid phase, end of simulation)' -suptitle 0 -cnum 5 -cformat .1e -d 10,8 -z 0 -s ,${slide[$x]},
  plopm -i 'FLOW1/FLOW1' -t "Flow ${versions[flow1]} - Flow ${versions[flow2]}, end of simulation" -v xco2l -clabel 'CO$_2$ mass fraction (liquid phase)' -cnum 5 -d 10,8 -z 0 -s ,${slide[$x]}, -diff FLOW2/FLOW2
  for quantity in tcpu msumlins msumnewt; do
    plopm -i 'FLOW1/FLOW1 FLOW2/FLOW2' -v $quantity -labels "Flow ${versions[flow1]}  Flow ${versions[flow2]}" -tunits ${units[$x]} -xformat .0f -yformat ${format[$quantity]}
  done
  plopm -i 'FLOW1/FLOW1 FLOW2/FLOW2' -v fgmip -labels "Flow ${versions[flow1]}  Flow ${versions[flow2]}" -tunits ${units[$x]} -xformat .0f -t "Total CO2 mass injected: ${total_mass[$x]} [kg]"
  cd ..
done

deactivate
