"""
    Copyright 2023 NORCE.

    This file is part of the Open Porous Media project (OPM).

    OPM is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    OPM is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OPM.  If not, see <http://www.gnu.org/licenses/>.

    Consult the COPYING file in the top-level source directory of this
    module for the precise wording of the license and the list of
    copyright holders.
"""
from CoolProp import CoolProp as cp
import numpy as np
from tqdm import tqdm
from mako.template import Template
import argparse


def generate_table(min_temp, max_temp, ntemp, min_pres, max_pres, npres, comp, tref=None, pref=None):
    """
    Generate OPM tables for a component

    Parameters
    ----------
    min_temp : float
        Min. temperature [K]
    max_temp : float
        Max. temperature [K]
    ntemp : int
        Number of temperature points
    min_pres : float
        Min. pressure [Pa]
    max_pres : float
        Max. pressure [Pa]
    npres : int
        Number of pressure points
    comp : str
        Component name, see http://www.coolprop.org/fluid_properties/PurePseudoPure.html
    tref : float, optional
        Reference temperature
    pref : float, optional
        Reference pressure
    """
    # Generate pressure and temperature values
    pres = np.linspace(min_pres, max_pres, npres)
    temp = np.linspace(min_temp, max_temp, ntemp)

    # Init. density and enthalpy output from Coolprops
    dens = np.zeros((ntemp, npres))  # kg/m3
    enth = np.zeros((ntemp, npres))  # J/kg

    # Instantiate progress bar
    pbar = tqdm(total=(temp.size * 2), ncols=100, desc='Progress')

    # Set reference temperature and pressure in Coolprop for enthalpy calculations
    if tref is not None and pref is not None:
        dmolar = cp.PropsSI('Dmolar', 'T', tref, 'P', pref, comp)
        cp.set_reference_state(comp, tref, dmolar, 0.0, 0.0)

    # Calculate density and enthalpy from Coolprops
    for i, t in enumerate(temp):
            # Density
            dens[i, :] = cp.PropsSI('D', 'T', t, 'P', pres, comp)
            pbar.update(1)

            # Enthalpy
            enth[i, :] = cp.PropsSI('H', 'T', t, 'P', pres, comp)
            pbar.update(1)
    
    # Generate template with mako
    mako_dict = {"minTemp": min_temp, "maxTemp": max_temp, "nTemp": ntemp, "minPress": min_pres, 
                 "maxPress" : max_pres, "nPress": npres, "density": dens, "enthalpy": enth, "comp": comp,
                 "refT" : tref, "refP" : pref}
    template = Template(filename='table_coolprop.mako')
    filled_template = template.render(**mako_dict)
    
    # Write <comp>tables.inc using the filled-out mako template
    with open(f'{comp.lower()}tables.inc', 'w', encoding='utf-8') as fid:
        fid.write(filled_template)


if __name__ == '__main__':
    #
    # CLI
    #
    parser = argparse.ArgumentParser(
        description="This script generates tables for a components' fluid properties \n"
        "(density and enthalpy) using CoolProp (http://www.coolprop.org).\n"
    )
    parser._optionals.title = 'arguments '
    parser.add_argument(
        "-t1", "--min_temp", required=True, type=float, help="The minimum temperature in K."
    )
    parser.add_argument(
        "-t2", "--max_temp", required=True, type=float, help="The maximum temperature in K."
    )
    parser.add_argument(
        "-nt",
        "--n_temp",
        required=True,
        type=int,
        help="The number of temperature sampling points."
        "min_temp is the first sampling point, max_temp the last.",
    )
    parser.add_argument(
        "-p1", "--min_press", required=True, type=float, help="The minimum pressure in Pascal."
    )
    parser.add_argument(
        "-p2", "--max_press", required=True, type=float, help="The maximum pressure in Pascal."
    )
    parser.add_argument(
        "-np",
        "--n_press",
        required=True,
        type=int,
        help="The number of pressure sampling points."
        "min_press is the first sampling point, max_press the last.",
    )
    parser.add_argument(
        "-c", "--comp_name", required=True, help="The component name, see CoolProp website."
    )
    parser.add_argument(
        "-tref", "--ref_temp", required=False, type=float, help="Reference temperature in K. [OPTIONAL]"
    )
    parser.add_argument(
        "-pref", "--ref_press", required=False, type=float, help="Reference pressure in K. [OPTIONAL]"
    )

    # Parse CLI arguments
    cmd_args = parser.parse_args()

    # Check if only one of tref and pref have been inputted
    if (cmd_args.ref_temp is not None and cmd_args.ref_press is None) or \
        (cmd_args.ref_temp is None and cmd_args.ref_press is not None):
        parser.error('-tref (or --ref_temp) and -pref (or --ref_press) must be given together!')

    # Run
    generate_table(min_temp=cmd_args.min_temp, max_temp=cmd_args.max_temp, ntemp=cmd_args.n_temp, 
                   tref=cmd_args.ref_temp, min_pres=cmd_args.min_press, max_pres=cmd_args.max_press, 
                   npres=cmd_args.n_press, pref=cmd_args.ref_press, comp=cmd_args.comp_name)
