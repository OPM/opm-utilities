#!/usr/bin/env bash
#
# A small script to run the opm-data cases to test two versions of OPM Flow,
# generating PNGs to compare the results. The resuls are saved in a folder name as
# the name of each case with two subfolders each (FLOW1 and FLOW2). Then plopm is used
# to generate plots of the spatial maps (oil saturation, modify below for a different
# quantity), performance quantities (msumlins, msumnewt, and tcpu), and additional
# summary vectors (fopr fgpr fopt fgpt fwpt fpr). Takes as arguments the path to the first
# flow executable (default "flow"), the second path (default "/path/to/coming/release"),
# number of cores to run OPM Flow (default "8"), and deck names from opm-data to
# run. For macOS, this requires to install bash (e.g., brew install bash).
#
# Example: Test the comming release located in /Users/build/opm-simulators/bin/flow
# with the current release using 32 CPUs for SPE10_MODEL2 and SLEIPNER_ORG.
#
#    bash opm-data-compare-opm-release.sh /Users/build/opm-simulators/bin/flow flow 32 SPE10_MODEL2 SLEIPNER_ORG
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
else
  source venv/bin/activate
fi
if ! command -v plopm >/dev/null 2>&1; then
  pip install git+https://github.com/cssr-tools/plopm.git
fi

declare -A flows versions view slide projection cases
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
view[1]="Side (i=1)"
view[2]="Front (j=1)"
view[3]="Top (k=1)"
slide[1]="1,,"
slide[2]=",1,"
slide[3]=",,1"
projection[1]=':,,'
projection[2]=',:,'
projection[3]=',,:'
m=0
for arg in "${@:4}"; do
  m=$((m + 1))
  cases[$m]=$arg
done

if [ ! -d "opm-data" ]; then
  git clone https://github.com/OPM/opm-data.git
  gunzip opm-data/sleipner/Sleipner_Reference_Model_cleaned.grdecl.gz
fi

for ((x = 1; x <= m; x++)); do
  case=${cases[$x]}
  if [ -d $case ]; then
    rm -rf $case
  fi
  mkdir $case
  deck="$(find "$PWD" -name $case.DATA)"
  # Add KEYWORDS to the SUMMARY
  if ! grep -q "PERFORMA" $deck; then
    sed -i.bak 's/^SUMMARY$/SUMMARY\
    PERFORMA\nFOPR\nFGPR\nFOPT\nFGPT\nFWPT\nFPR/' $deck
    sed -i.bak "s|SUMMARY |SUMMARY\nPERFORMA\nFOPR\nFGPR\nFOPT\nFGPT\nFWPT\nFPR |g" $deck
    rm -f $deck.bak
  fi
  n=1
  for flow in flow1 flow2; do
    if grep -q ":" <<< ${flows[$flow]}; then
      mkdir -p $case/FLOW$n
      DECK_DIR=$(dirname ${deck})
      DECK=$(basename ${deck})
      docker run -v ${PWD}/$case/FLOW$n:/shared_host -v ${DECK_DIR}:/deck ${flows[$flow]} mpirun -np $CPUS flow /deck/$DECK --output-dir=/shared_host --parsing-strictness=low --check-satfunc-consistency=0
    else
      mpirun -np $CPUS ${flows[$flow]} $deck --output-dir=$case/FLOW$n --parsing-strictness=low --check-satfunc-consistency=0
    fi
    n=$((n + 1))
  done
  cd $case
  # Spatial maps for oil saturation (modify this for a different quantity, i.e., pressure)
  for ((i = 1; i <= 3; i++)); do
    plopm -i 'FLOW1/ FLOW2/' -subfigs 2,1 -t "Flow ${versions[flow1]}  Flow ${versions[flow2]}" -cbsfax 0.25,0.93,0.5,0.02 -delax 1 -v soil -clabel "${view[$i]} oil saturation (end of simulation)" -suptitle 0 -cnum 5 -cformat .1e -d 10,8 -z 0 -s "${slide[$i]}" -save slide$i
    plopm -i 'FLOW1/' -v soil -cnum 5 -d 10,8 -z 0 -diff 'FLOW2/' -s "${slide[$i]}" -t "${view[$i]} oil saturation (Flow ${versions[flow1]}-Flow ${versions[flow2]}, end of simulation)" -save diff_slide$i
    plopm -i 'FLOW1/ FLOW2/' -subfigs 2,1 -t "Flow ${versions[flow1]}  Flow ${versions[flow2]}" -cbsfax 0.25,0.93,0.5,0.02 -delax 1 -v soil -clabel "${view[$i]} pore volume weighted oil saturation projection (end of simulation)" -suptitle 0 -cnum 5 -cformat .1e -d 10,8 -z 0 -s "${projection[$i]}" -save projection$i
    plopm -i 'FLOW1/' -v soil -cnum 5 -d 10,8 -z 0 -diff 'FLOW2/' -t "${view[$i]} pore volume weighted oil saturation projection (Flow ${versions[flow1]}-Flow ${versions[flow2]}, end of simulation)" -s "${projection[$i]}" -save diff_projection$i
  done
  for quantity in tcpu msumlins msumnewt fopr fgpr fopt fgpt fwpt fpr; do
    plopm -i "FLOW1/ FLOW2/" -v $quantity -labels "Flow ${versions[flow1]}  Flow ${versions[flow2]}" -tunits y -xformat .0f
  done
  cd ..
done

deactivate
