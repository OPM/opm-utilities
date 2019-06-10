# OPMRUN
OPMRUN is graphical user interface to Flow that has similar functionality to the commercial simulator’s ECLRUN program. Target audience are Reservoir Engineers in a production environment. Developers and experienced Linux users will already have compatible work flows.

Allows editing and management of OPM Flow’s run time parameters. Default parameters are automatically loaded from OPM Flow, and the user can reset the default set either from a parameter or PRT file. Editing of a job’s parameter file is also available.

Allows simulation jobs to be queued and run in either foreground (under OPMRUN), or background (in an xterm terminal session). Jobs in the queue can be set to run in NOSIM mode or RUN mode.
Foreground jobs can be killed from OPMRUN.

Queues can be edited, saved and loaded.

Jobs can be compressed to save space (DATA , and all OPM Flow output files) and uncompressed.
Written in Python 3 and tested under Unbuntu-Mate 18.04 TLS.

Compiled binary version should work on all Linux systems, no need to install dependencies or Python.

Notes:
------
PySimpleGUI is the GUI tool used to build OPMRUN. It is in active development and is frequently updated for fixes and new features. This version of OPMRUN used verion 3.36.0 of PySimpleGUI, later and older   versions of PySimpleGUI may not work. Each release of OPMRUN will update to the latest release of PySimpleGUI. In addition, the following modules are require:
            
( 1) PySimpleGUI
( 2) datetime
( 3) getpass
( 4) os
( 5) sys
( 6) psutil
( 7) re
( 8) subprocess
( 9) pathlib





