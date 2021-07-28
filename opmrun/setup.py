import setuptools
from opmrun import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='opmrun',
    version=__version__,
    author='David Baxendale',
    author_email='david.baxendale@eipc.co',
    description='OPMRUN a GUI for OPM Flow',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/OPM/opm-utilities/tree/master/opmrun',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License, version 3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=['airspeed', 'pandas', 'psutil', 'pyDOE2', 'PySimpleGUI'],
    python_requires='>=3.6'
)

