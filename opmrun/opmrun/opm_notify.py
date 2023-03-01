# =======================================================================================================================
#
"""OPM_NOTIFY.py - Send Notification Message to Desktop

The module is used in OPMRUN background scripts to send a status notification message to the host desktop.

Program Documentation
--------------------
Only Python 3 is supported and tested Python2 support has been depreciated.

2021.07.01 - New module initial release.

Copyright Notice
----------------
This file is part of the Open Porous Media project (OPM).

OPM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OPM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the aforementioned GNU General Public Licenses for more
details.

Copyright (C) 2018-2021 Equinox International Petroleum Consultants Pte Ltd.

Author  : David Baxendale
          david.baxendale@eipc.co
Version : 2021.07.01
Date    : 31-July-2021
"""
# ----------------------------------------------------------------------------------------------------------------------
# 3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8         9         0         1         2
#        0         0         0         0         0         0         0         0         0         1         1         1
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Import Modules and Start Up Section
# ----------------------------------------------------------------------------------------------------------------------
import sys
import os
from pathlib import Path
#
# Import Required Non-Standard Modules
#
from notifypy import Notify

# ----------------------------------------------------------------------------------------------------------------------
# Define Modules Section
# ----------------------------------------------------------------------------------------------------------------------
def opm_notify_main():
    """Main function for Sending Notification Message to the Host Desktop

    The function is used in OPMRUN background scripts to send a status notification message to the host desktop, based
    on the augments supplied to the function, there are no parameters for this function. The function is used on a
    standalone basis and thus does not use the OPMRUN system variable directory.

    Augments
    --------
    --title= : str
        The title to be used in the notification. If default with '' then 'OPMRUN Background Processing", will be used.
    --message= : dict
        The message to be displayed in the notification, should normally the job number and job name.
    --status= : int
        Status code used to display the icon in the notification set to one of the following:
            ''   : for the default icon opmrun.png
            "0"  : for pass and the opm_notify_pass.png icon
            "0"  : for fail and the opm_notify_fail.png icon.

    Parameters
    ----------
    None

    Returns
    -------
    Issues notification message to the desktop.
    """

    #
    # Read Arguments
    #
    title    = ''
    message  = ''
    pathdir  = os.path.dirname(os.path.abspath(__file__))
    icon     = Path(pathdir) / 'opmrun.png'
    iconpass = Path(pathdir) / 'opmrun-pass.png'
    iconfail = Path(pathdir) / 'opmrun-fail.png'
    for cmd in sys.argv:
        if '--title=' in cmd:
            title = cmd.replace('--title=', '')
            if title is None:
                title = 'OPMRUN Background Processing'
        elif '--message=' in cmd:
            message = cmd.replace('--message=', '')
        elif '--status=' in cmd:
            status = cmd.replace('--status=', '')
            if status == '0':
                icon = iconpass
            elif status == '1':
                icon = iconfail

    notification                  = Notify()
    notification.application_name = 'OPMRUN Background Processing',
    notification.title            = str(title)
    notification.message          = str(message)
    notification.icon             = icon
    notification.send(block=False)

if __name__ == '__main__':
    opm_notify_main()

# ======================================================================================================================
# End of """OPM_NOTIFY.py
# ======================================================================================================================
