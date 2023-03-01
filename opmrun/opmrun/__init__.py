from opmrun import *
from opmrun.opm_common import (copy_to_clipboard, convert_string, get_time, kill_job, set_gui_options, opm_popup, print_dict,
                        remove_ansii_escape_codes, run_command, tail, wsl_path)
from opmrun.opm_compress import (change_directory, compress_cmd, compress_files, uncompress_files)
from opmrun.opm_keyw import keyw_main
from opmrun.opm_sensitivity import *
from opmrun.opm_prodsched import *
from opmrun.opm_wellspec import wellspec_main
from opmrun.opm_welltraj import welltraj_main

__version__ = '2021.4.1'
