"""
@author:   Ken Venner
@contact:  ken@venerllc.com
@version: 1.14

Utility used to readn and write files from

"""

import os.path
import os
import kvdate
import logging

### GLOBAL VARIABLES AND CONVERSIONS ###


def read_pool_heater_allowable_file(
    input_file: str, logger: logging.Logger | None = None
) -> tuple[list, list]:
    """
    if file exists, read in the file and convert each line to a date and build a list of dates
    that we will not flag the pool is enabled and attempt to turn it off

    Input:
        input_file - file/path to the filename of dates that the pool is enabled to be turned on
        logger - logger object - used to write out to the log file

    Returns
        pool_heater_allowed - list - of valid dates the pool can be enabled
        pool_heater_invalid_dates - list - of lines in the date file that could not convert into dates, and there error message during conversion

    """
    pool_heater_allowed = []
    pool_heater_invalid_dates = []

    # no file - so no inputs
    if not os.path.exists(input_file):
        if logger:
            logger.info(input_file + " not found")
        return pool_heater_allowed, pool_heater_invalid_dates

    # get the file read in the lines and convert the string to date
    with open(input_file, "r") as file:
        # Read each line in the file
        for idx, line in enumerate(file):
            try:
                pool_heater_allowed.append(
                    kvdate.datetime_from_str(line.strip()).date()
                )
            except Exception as e:
                pool_heater_invalid_dates.append(f"{idx + 1}|{line.strip()}|{e}")

    if logger:
        logger.info(
            str(len(pool_heater_allowed)) + " dates allowed to have pool enabled"
        )
    return pool_heater_allowed, pool_heater_invalid_dates


# eof
