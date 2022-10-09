"""
SaltStack extension for SAPCAR
Copyright (C) 2022  Benjamin Wegener

SAPCAR execution modules
========================
Execution modules to manage SAPCAR archives

:codeauthor: Benjamin Wegener <wegener.benjamin@googlemail.com>
:maturity:   new
:depends:    N/A
:platform:   Linux

.. note::
    Only Linux is supported as platform and SAPCAR must be available in the PATH.
    Reference: http://www.easymarketplace.de/SAPCAR.php#OnlineHelp
"""
# python imports
import logging
import os

import salt.utils.path
import salt.utils.platform

# global variables
log = logging.getLogger(__name__)

__virtualname__ = "sap_car"

__func_alias__ = {
    "list_": "list",
}


def __virtual__():
    """
    Only works on Linux and if SAPCAR is available in PATH
    """
    if salt.utils.platform.is_windows():
        return (
            False,
            f"The {__virtualname__} execution module failed to load, Windows systems are not supported.",
        )
    if not salt.utils.path.which("SAPCAR"):
        return (
            False,
            f"The {__virtualname__} execution module failed to load, SAPCAR binary is not in the path.",
        )
    return __virtualname__


def list_(path, options=None, user=None, group=None):
    """
    Execute SAPCAR command to list the files of a SAP CAR or SAR archive files.
    If user / group are provided it will be executed with this user / group.

    path
        Path to the sar file to be extracted

    options
        Additional options to SAPCAR command

    user
        User to execute the SAPCAR command

    group
        Group to execute

    CLI Example:

    .. code-block:: bash

        salt '*' sap_car.list path=/mnt/nfs/kernel.sar
    """
    log.debug(f"Running function for path {path}")

    if not user:
        user = __grains__["username"]
    if not group:
        group = __grains__["groupname"]

    if not os.path.isfile(path):
        raise Exception(f"The SAR file '{path}' does not exist")

    options_str = f" {options}" if options else ""

    cmd = f"SAPCAR -tf {path}{options_str}"

    cmd_ret = __salt__["cmd.run_all"](cmd, runas=user, group=group, python_shell=True, timeout=600)
    log.debug(f"Output:\n{cmd_ret}")
    if cmd_ret.get("retcode"):
        out = cmd_ret.get("stderr").strip()
        log.error(f"Could not list files of archive {path}:\n{out}")
        return False
    out = cmd_ret.get("stdout").splitlines()[
        1:
    ]  # first line is always "SAPCAR: processing archive XYZ (version 2.01)"
    file_list = []
    for line in out:
        # each line looks like this: "-rw-------        5006    18 Sep 2020 11:58 SIGNATURE.SMF"
        file_list.append(
            line.split(" ")[-1]
        )  # right now, we are only interested in the last element
    return file_list


def extract(path, files=None, options=None, output_dir=None, user=None, group=None):
    """
    Execute SAPCAR command to decompress a SAP CAR or SAR archive files.
    If user / group are provided it will be executed with this user / group.

    path
        Path to the sar file to be extracted

    files
        List of files to extract from the archive; if None (default), all files will be extracted

    options
        Additional options to SAPCAR command

    output_dir
        Directory where archive will be extracted. It creates the dir if the path doesn't exist. If
        it's not set the current dir is used

    user
        User to execute the SAPCAR command

    group
        Group to execute

    CLI Example:

    .. code-block:: bash

        salt '*' sap_car.extract path=/mnt/nfs/kernel.sar output_dir=/sapmnt/A01/SYS/ user=a01adm group=sapsys
    """
    log.debug(f"Running function for path {path}")

    if not user:
        user = __grains__["username"]
    if not group:
        group = __grains__["groupname"]

    if not os.path.isfile(path):
        raise Exception(f"The SAR file '{path}' does not exist")

    options_str = f" {options}" if options else ""
    output_dir_str = output_dir if output_dir else ""
    files = " ".join(files) if files else ""

    cmd = f"SAPCAR -xvf {path}{options_str} -manifest SIGNATURE.SMF -R {output_dir_str} {files}"

    cmd_ret = __salt__["cmd.run_all"](cmd, runas=user, group=group, python_shell=True, timeout=600)
    log.debug(f"Output:\n{cmd_ret}")
    if cmd_ret.get("retcode"):
        out = cmd_ret.get("stderr").strip()
        log.error(f"Could not extract {path}:\n{out}")
        return False
    return True
