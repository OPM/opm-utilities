# PVT tables

Generate PVT tables with Coolprop Python package.

**_OBS_**: Only density and enthalpy tables at the moment.

## Setup

Generate a [virtual environment](https://docs.python.org/3/library/venv.html) (strongly recommended) and install
requirements:

```python
pip install -r requirements.txt
```

## Usage

To get the program help page:

```python
python3 opm_tables_coolprop.py -h
```

The output from the program is a ```<comp>tables.inc``` file where ```comp``` is the component name. The include file
can be used to replace ```co2tables.inc``` or ```h2tables.inc``` in ```opm-common```, or generate new tables for other
components.

## Example

To generate tables for CO2 at temperature and pressure ranges of ```T = [300 K, 400 K]``` and ```P = [1e5 Pa, 100e5
Pa]```, respectively, with 100 points in each :

```python
python3 opm_tables_coolprop.py -t1 300 -t2 400 -nt 100 -p1 1e5 -p2 100e5 -np 100 -c CO2
```

## Dependencies

* [Coolprop](http://www.coolprop.org/)
* [Mako](https://www.makotemplates.org/)
* [Numpy](https://numpy.org/)
