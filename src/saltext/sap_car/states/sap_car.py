"""
SaltStack extension for SAPCAR
Copyright (C) 2022  Benjamin Wegener

SAPCAR States
=============
States to manage SAPCAR archives

:codeauthor: Benjamin Wegener
:maturity:   new
:depends:    N/A
:platform:   Linux

This module can be used to ensure that files from a SAPCAR archive are extracted. The state
``extracted`` will check for file existance based on the list of files in the archive, but
NOT based on content or hash!

.. code-block:: jinja

    SAProuter is extracted:
      sap_car.extracted:
        - name: /mnt/nfs/saprouter.sar
        - output_dir: /usr/sap/saprouter/
        - user: root
        - group: root
        - require:
          - pkg: SAPCAR is installed

.. note::
    Even though there are no python dependencies, SAPCAR must be available in the PATH.

For more information on SAPCAR, see http://www.easymarketplace.de/SAPCAR.php.
"""
import logging

import salt.utils.files

# Globals
log = logging.getLogger(__name__)

__virtualname__ = "sap_car"


def __virtual__():
    """
    Only works on Linux and if SAPCAR is available in PATH
    """
    if __virtualname__ not in __salt__:
        return (
            False,
            f"The {__virtualname__} execution module failed to load.",
        )
    return __virtualname__


def extracted(name, options=None, output_dir=None, user=None, group=None):
    """
    Extracts a SAPCAR archive if necessary.

    name
        Path to the sar file to be extracted

    options
        Additional options to SAPCAR command

    output_dir
        Directory where archive will be extracted. It creates the dir if the path doesn't exist. If
        it's not set the current dir is used

    user
        User to execute the SAPCAR command

    group
        Group to execute
    """
    log.debug(f"Running function with name={name}")
    ret = {
        "name": name,
        "changes": {"old": [], "new": []},
        "result": True if not __opts__["test"] else None,
        "comment": "",
    }

    log.debug("Listing files of archive")
    archive_file_list = __salt__["sap_car.list"](
        path=name, output_dir=output_dir, user=user, group=group
    )
    if not isinstance(archive_file_list, list):
        log.error("An error occured during list of files")
        ret["comment"] = "An error occured during list of files, check the log files"
        ret["result"] = False
        return ret

    log.debug("Listing files of target dir")
    disk_file_list = salt.utils.files.list_files(output_dir)  # returns full paths
    disk_file_list.remove(output_dir)  # is part of list by default
    disk_file_list = [x.replace(output_dir, "") for x in disk_file_list]

    log.debug("Checking if files need to be extracted")
    files_to_extract = []
    for archive_file in archive_file_list:
        if archive_file not in disk_file_list:
            files_to_extract.append(archive_file)
        else:
            disk_file_list.remove(archive_file)  # should increase performance for large archives
    if not files_to_extract:
        log.debug("All files are already extracted")
        ret["comment"] = "All files are already extracted"
        ret["result"] = True
        ret["changes"] = {}
        return ret

    if files_to_extract == archive_file_list:
        log.debug("All files need to be extracted")
        files_to_extract = None

    log.debug("Extracting files")
    if __opts__["test"]:
        ret["comment"] = f"Extracted archive {name} to {output_dir}"
        if files_to_extract:
            ret["changes"]["new"] = f"Would extract the following files:\n{files_to_extract}"
        else:
            ret["changes"]["new"] = f"Would extract all files from {name}"
        ret["result"] = None
    else:
        result = __salt__["sap_car.extract"](
            path=name,
            files=files_to_extract,
            options=options,
            output_dir=output_dir,
            user=user,
            group=group,
        )
        if not isinstance(result, bool):
            log.error(f"An error occured during execution:\n{result}")
            ret["comment"] = "An error occured during execution, check the log files"
            ret["result"] = False
            return ret
        if not result:
            log.error(f"Could not extract archive {name}")
            ret["comment"] = f"Could not extract archive {name}"
            ret["result"] = False
        else:
            ret["comment"] = f"Extracted archive {name} to {output_dir}"
            if files_to_extract:
                ret["changes"]["new"] = files_to_extract
            else:
                ret["changes"]["new"] = f"Extracted all files from {name}"
            ret["result"] = True

    if not ret["changes"]["new"]:
        del ret["changes"]["new"]
    if not ret["changes"]["old"]:
        del ret["changes"]["old"]

    log.debug(f"Returning:\n{ret}")
    return ret
