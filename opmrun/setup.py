import setuptools
from opmrun import __version__

with open("DESCRIPTION.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    #
    # Project Information
    #
    name='opmrun',
    version=__version__,
    author='David Baxendale',
    author_email='david.baxendale@eipc.co',
    maintainer='David Baxendale',
    maintainer_email='david.baxendale@eipc.co',
    description='OPMRUN a GUI for OPM Flow',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/OPM/opm-utilities/tree/master/opmrun',
    license='GNU General Public License Version 3, 29 June 2007',
    license_files='LICENSE.txt',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License, version 3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    #
    # Package Data and Requirements
    #
    python_requires='>=3.6',
    install_requires=['airspeed', 'numpy', 'pandas', 'psutil', 'pyDOE2', 'PySimpleGUI'],
    entry_points={
        'gui_scripts': [
            'opmrun=opmrun.opmrun:main'
        ],
    },
    packages=setuptools.find_packages(),
    package_data={
        # Specify non-Python files to include in the package
        'opmrun': [
            '*.png',  # Include all PNG files
            '*.ico',  # Include all ICO files
        ],
    },
)
