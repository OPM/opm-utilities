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
struct ${comp}TabulatedDensityTraits {
    typedef double Scalar;
    static const char  *name;
    static const int    numX = ${nTemp};
    static const Scalar xMin;
    static const Scalar xMax;
    static const int    numY = ${nPress};
    static const Scalar yMin;
    static const Scalar yMax;

    static const Scalar vals[${nTemp}][${nPress}];
};

inline const double ${comp}TabulatedDensityTraits::xMin = ${'{0:.15e}'.format(minTemp)};
inline const double ${comp}TabulatedDensityTraits::xMax = ${'{0:.15e}'.format(maxTemp)};
inline const double ${comp}TabulatedDensityTraits::yMin = ${'{0:.15e}'.format(minPress)};
inline const double ${comp}TabulatedDensityTraits::yMax = ${'{0:.15e}'.format(maxPress)};
inline const char  *${comp}TabulatedDensityTraits::name = "density";

inline const ${comp}TabulatedDensityTraits::Scalar ${comp}TabulatedDensityTraits::vals[${nTemp}][${nPress}] =
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

struct ${comp}TabulatedEnthalpyTraits {
    typedef double Scalar;
    static const char  *name;
    static const int    numX = ${nTemp};
    static const Scalar xMin;
    static const Scalar xMax;
    static const int    numY = ${nPress};
    static const Scalar yMin;
    static const Scalar yMax;
    static const Scalar vals[${nTemp}][${nPress}];
};

inline const double ${comp}TabulatedEnthalpyTraits::xMin = ${'{0:.15e}'.format(minTemp)};
inline const double ${comp}TabulatedEnthalpyTraits::xMax = ${'{0:.15e}'.format(maxTemp)};
inline const double ${comp}TabulatedEnthalpyTraits::yMin = ${'{0:.15e}'.format(minPress)};
inline const double ${comp}TabulatedEnthalpyTraits::yMax = ${'{0:.15e}'.format(maxPress)};
inline const char  *${comp}TabulatedEnthalpyTraits::name = "enthalpy";

inline const ${comp}TabulatedEnthalpyTraits::Scalar ${comp}TabulatedEnthalpyTraits::vals[${nTemp}][${nPress}] =
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

typedef Opm::UniformTabulated2DFunction< double > TabulatedFunction;

// this class collects all the ${comp}tabulated quantities in one convenient place
struct ${comp.upper()}Tables {
   static const TabulatedFunction   tabulatedEnthalpy;
   static const TabulatedFunction   tabulatedDensity;
   static constexpr double brineSalinity = 1.000000000000000e-01;
};

inline const TabulatedFunction ${comp.upper()}Tables::tabulatedEnthalpy
    {${comp}TabulatedEnthalpyTraits::xMin,
     ${comp}TabulatedEnthalpyTraits::xMax,
     ${comp}TabulatedEnthalpyTraits::numX,
     ${comp}TabulatedEnthalpyTraits::yMin,
     ${comp}TabulatedEnthalpyTraits::yMax,
     ${comp}TabulatedEnthalpyTraits::numY,
     ${comp}TabulatedEnthalpyTraits::vals};

inline const TabulatedFunction ${comp.upper()}Tables::tabulatedDensity
    {${comp}TabulatedDensityTraits::xMin,
     ${comp}TabulatedDensityTraits::xMax,
     ${comp}TabulatedDensityTraits::numX,
     ${comp}TabulatedDensityTraits::yMin,
     ${comp}TabulatedDensityTraits::yMax,
     ${comp}TabulatedDensityTraits::numY,
     ${comp}TabulatedDensityTraits::vals};


#endif /* ${comp.upper()}TABLES_INC */
