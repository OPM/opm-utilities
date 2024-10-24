#ifndef ${comp.upper()}TABLES_INC
#define ${comp.upper()}TABLES_INC

/* The data has been calculated using the CoolProp Python package https://doi.org/10.1021/ie4033999.
*
* THIS AN AUTO-GENERATED FILE! DO NOT EDIT IT!
*
* Bell, Ian H. and Wronski, Jorrit and Quoilin, Sylvain and Lemort, Vincent
* Pure and Pseudo-pure Fluid Thermophysical Property Evaluation and
* the Open-Source Thermophysical Property Library CoolProp
* Industrial & Engineering Chemistry Research, 53(6), 2014
* DOI: 10.1021/ie4033999
*
* Temperature range: ${'{0:.3f}'.format(minTemp)} K to ${'{0:.3f}'.format(maxTemp)} K, using ${nTemp} sampling points
* Pressure range: ${'{0:.3f}'.format(minPress/1e6)} MPa to ${'{0:.3f}'.format(maxPress/1e6)} MPa, using ${nPress} sampling points
% if refP is not None and refT is not None:
* Reference temperature and pressure: ${refT} K and ${refP/1e6} MPa
% else:
* Reference state from Coolprop website (http://www.coolprop.org/coolprop/HighLevelAPI.html#reference-states):
*   Enthalpy = 200 kJ/kg (and entropy = 1 kJ/kg/K) at 0C saturated liquid
% endif
*
* Generated using opm_tables_coolprop.py in opm-utilities like this:
*
% if refP is None and refT is None:
* >> python3 opm_tables_coolprop.py -t1 ${minTemp} -t2 ${maxTemp} -nt ${nTemp} -p1 ${minPress} -p2 ${maxPress} -np ${nPress} -c ${comp}
% else:
* >> python3 opm_tables_coolprop.py -t1 ${minTemp} -t2 ${maxTemp} -nt ${nTemp} -tref ${refT} -p1 ${minPress} -p2 ${maxPress} -np ${nPress} -pref ${refP} -c ${comp}
% endif
* 
*/
// Fill in the data for a struct like this (intended to work together with brine salinity 0.1)
//struct Opm::${comp}TabulatedDensityTraits {
//    typedef double Scalar;
//    static const char  *name;
//    static const int    numX = ${nTemp};
//    static const Scalar xMin;
//    static const Scalar xMax;
//    static const int    numY = ${nPress};
//    static const Scalar yMin;
//    static const Scalar yMax;
//    static const Scalar vals[${nTemp}][${nPress}];
//};

inline const double Opm::${comp}TabulatedDensityTraits::xMin = ${'{0:.15e}'.format(minTemp)};
inline const double Opm::${comp}TabulatedDensityTraits::xMax = ${'{0:.15e}'.format(maxTemp)};
inline const double Opm::${comp}TabulatedDensityTraits::yMin = ${'{0:.15e}'.format(minPress)};
inline const double Opm::${comp}TabulatedDensityTraits::yMax = ${'{0:.15e}'.format(maxPress)};
inline const char  *Opm::${comp}TabulatedDensityTraits::name = "density";

inline const Opm::${comp}TabulatedDensityTraits::Scalar Opm::${comp}TabulatedDensityTraits::vals[${nTemp}][${nPress}] =
{
% for i in range(nTemp):
${'\t{'}
% for j in range(nPress):
%if (j+1) % 5 == 0:
${'\t\t{0:.15e}'.format(density[i][j])}${'\n' if loop.last else ',\n'}\
%else:
${'\t\t{0:.15e}'.format(density[i][j])}${'\n' if loop.last else ','}\
%endif
% endfor
${'\t}' if loop.last else '\t},'}
% endfor
};

// Fill in the data for a struct like this (intended to work together with brine salinity 0.1)
//struct Opm::${comp}TabulatedEnthalpyTraits {
//    typedef double Scalar;
//    static const char  *name;
//    static const int    numX = ${nTemp};
//    static const Scalar xMin;
//    static const Scalar xMax;
//    static const int    numY = ${nPress};
//    static const Scalar yMin;
//    static const Scalar yMax;
//    static const Scalar vals[${nTemp}][${nPress}];
//};

inline const double Opm::${comp}TabulatedEnthalpyTraits::xMin = ${'{0:.15e}'.format(minTemp)};
inline const double Opm::${comp}TabulatedEnthalpyTraits::xMax = ${'{0:.15e}'.format(maxTemp)};
inline const double Opm::${comp}TabulatedEnthalpyTraits::yMin = ${'{0:.15e}'.format(minPress)};
inline const double Opm::${comp}TabulatedEnthalpyTraits::yMax = ${'{0:.15e}'.format(maxPress)};
inline const char  *Opm::${comp}TabulatedEnthalpyTraits::name = "enthalpy";

inline const Opm::${comp}TabulatedEnthalpyTraits::Scalar Opm::${comp}TabulatedEnthalpyTraits::vals[${nTemp}][${nPress}] =
{
% for i in range(nTemp):
${'\t{'}
% for j in range(nPress):
%if (j+1) % 5 == 0:
${'\t\t{0:.15e}'.format(enthalpy[i][j])}${'\n' if loop.last else ',\n'}\
%else:
${'\t\t{0:.15e}'.format(enthalpy[i][j])}${'\n' if loop.last else ','}\
%endif
% endfor
${'\t}' if loop.last else '\t},'}
% endfor
};

#endif /* ${comp.upper()}TABLES_INC */
