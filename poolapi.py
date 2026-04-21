"""
@author:   Ken Venner
@contact:  ken@venerllc.com
@version: 1.03

using the screenlogicpy routine - talk with the pool control
and either get values or set heater temperature or turn on/off the heater

"""

import asyncio
from screenlogicpy import ScreenLogicGateway
import logging

import pprint

DEBUG = False


# If your gateway's IP/port is known, you can specify them:
GATEWAY_IP = "192.168.8.141"  # or None to auto-discover
GATEWAY_PORT = 2198  # default ScreenLogic port

POOL_DEVICE = 0
SPA_DEVICE = 1

GET_DATA_4_SETTING = {
    "pool_temp_last": ["body", POOL_DEVICE, "last_temperature", "value"],
    "pool_temp_set": ["body", POOL_DEVICE, "heat_setpoint", "value"],
    "pool_heat_set": ["body", POOL_DEVICE, "heat_state", "value"],
    "pool_heat_mode": ["body", POOL_DEVICE, "heat_mode", "value"],
    "spa_temp_last": ["body", SPA_DEVICE, "last_temperature", "value"],
    "spa_temp_set": ["body", SPA_DEVICE, "heat_setpoint", "value"],
    "spa_heat_set": ["body", SPA_DEVICE, "heat_state", "value"],
    "spa_heat_mode": ["body", SPA_DEVICE, "heat_mode", "value"],
}
GET_ENUM_4_SETTING = {
    "pool_heat_set": ["body", POOL_DEVICE, "heat_state", "enum_options"],
    "pool_heat_mode": ["body", POOL_DEVICE, "heat_mode", "enum_options"],
    "spa_heat_set": ["body", SPA_DEVICE, "heat_state", "enum_options"],
    "spa_heat_mode": ["body", SPA_DEVICE, "heat_mode", "enum_options"],
}


async def read_screenlogic(
    ip: str = GATEWAY_IP,
    disp_msg: bool | None = None,
    logger: logging.Logger | None = None,
) -> tuple[list, list]:
    """
    Read data from a device based on the IP passed in
    Get the temperature and heater settings

    return the results array
    and the keys to those results array

    Inputs:
        ip - str - the IP address of the pool controller
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:
        result_values - list - of result values
        result_keys - list - of the keys to those values


    """

    # return a dict of results
    result_keys = []
    result_values = []

    # Initialize gateway (specify IP/port to skip discovery)
    gateway = ScreenLogicGateway()

    try:
        # connect to it
        await gateway.async_connect(ip)

        if disp_msg:
            print("Successfully connected to ScreenLogic")

        # get the data
        await gateway.async_update()

        # display the full results
        if disp_msg:
            print("get_data dump:")
            pprint.pprint(gateway.get_data())
            print("-" * 80)

        # get the conversion data
        enum_lookup = {}
        for k, v in GET_ENUM_4_SETTING.items():
            enum_lookup[k] = gateway.get_data(*v)

        # debugging
        if DEBUG:
            pprint.pprint(enum_lookup)
            print("-" * 80)

        # read in the attributes we care about
        for k, v in GET_DATA_4_SETTING.items():
            value = gateway.get_data(*v)
            if k in enum_lookup:
                value = enum_lookup[k][value]
            result_keys.append(k)
            result_values.append(value)
            # dictionary
            # results[k] = value

            # debugging
            if DEBUG:
                print(k, value)

        # debugging
        if DEBUG:
            print("-" * 80)

    except Exception as e:
        if logger:
            logger.error("Error communicating with pool controller: %s", e)
        else:
            print("Error communicating with ScreenLogic:", e)
    finally:
        await gateway.async_disconnect()

    return result_values, result_keys


async def set_heat_mode_pool(
    ip: str = GATEWAY_IP,
    mode: int = 0,
    disp_msg: bool = False,
    logger: logging.Logger | None = None,
) -> None:
    """
    turn on and turn off the heater on the pool based on IP

    Inputs:
        ip - str - the IP address of the pool controller
        mode - int - if zero - turn off the heat, any other number turn it on
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:

    """

    # Initialize gateway (specify IP/port to skip discovery)
    gateway = ScreenLogicGateway()

    # if they gave a value - set it to 3 which turns on the heater
    if mode:
        mode = 3

    try:
        # connect to it
        await gateway.async_connect(ip)

        # display message if enabled
        if disp_msg:
            print("Successfully connected to ScreenLogic")

        # get the data
        await gateway.async_update()

        # now set the mode
        await gateway.async_set_heat_mode(POOL_DEVICE, mode)

    except Exception as e:
        if logger:
            logger.error("Error communicating with pool controller: %s", e)
        else:
            print("Error communicating with ScreenLogic:", e)

    finally:
        await gateway.async_disconnect()


async def set_heat_mode_spa(
    ip: str = GATEWAY_IP,
    mode: int = 0,
    disp_msg: bool = False,
    logger: logging.Logger | None = None,
) -> None:
    """
    turn on and turn off the heater on the spa based on IP

    Inputs:
        ip - str - the IP address of the pool controller
        mode - int - if zero - turn off the heat, any other number turn it on
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:

    """

    # display message
    if disp_msg:
        print(ip, mode, SPA_DEVICE, disp_msg)

    # Initialize gateway (specify IP/port to skip discovery)
    gateway = ScreenLogicGateway()

    # if they gave a value - set it to 3 which turns on the heater
    if mode:
        mode = 3

    # display message
    if disp_msg:
        print("gateway created")

    try:
        # connect to it
        await gateway.async_connect(ip)

        if disp_msg:
            print("Successfully connected to ScreenLogic")

        # get update
        await gateway.async_update()

        # display message
        if disp_msg:
            print("update")

        # now set the mode
        await gateway.async_set_heat_mode(SPA_DEVICE, mode)

    except Exception as e:
        if logger:
            logger.error("Error communicating with pool controller: %s", e)
        else:
            print("Error communicating with ScreenLogic:", e)
    finally:
        await gateway.async_disconnect()


async def set_spa_temp(
    ip: str = GATEWAY_IP,
    desired_temp: int = 100,
    disp_msg: bool = False,
    logger: logging.Logger | None = None,
) -> None:
    """
    set the temperature on the spa

    Inputs:
        ip - str - the IP address of the pool controller
        desired_temp - int - the temperature to set the spa to
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:


    """

    # display message
    if disp_msg:
        print(ip, desired_temp, SPA_DEVICE, disp_msg)

    # Initialize gateway (specify IP/port to skip discovery)
    gateway = ScreenLogicGateway()

    # display message
    if disp_msg:
        print("gateway created")

    try:
        # connect to it
        await gateway.async_connect(ip)

        # display message
        if disp_msg:
            print("Successfully connected to ScreenLogic")

        # get update
        await gateway.async_update()

        # display message
        if disp_msg:
            print("update")

        # now set the mode
        await gateway.async_set_heat_temp(SPA_DEVICE, desired_temp)

    except Exception as e:
        if logger:
            logger.error("Error communicating with pool controller: %s", e)
        else:
            print("Error communicating with ScreenLogic:", e)
    finally:
        await gateway.async_disconnect()


async def set_pool_temp(
    ip: str = GATEWAY_IP,
    desired_temp: int = 84,
    disp_msg: bool = False,
    logger: logging.Logger | None = None,
) -> None:
    """
    Set the pool temperature

    Inputs:
        ip - str - the IP address of the pool controller
        desired_temp - int - the temperature to set the spa to
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:

    """

    # display message
    if disp_msg:
        print(ip, desired_temp, SPA_DEVICE, disp_msg)

    # Initialize gateway (specify IP/port to skip discovery)
    gateway = ScreenLogicGateway()

    # display message
    if disp_msg:
        print("gateway created")

    try:
        # connect to it
        await gateway.async_connect(ip)

        # display message
        if disp_msg:
            print("Successfully connected to ScreenLogic")

        # get update
        await gateway.async_update()

        # display message
        if disp_msg:
            print("update")

        # now set the mode
        await gateway.async_set_heat_temp(POOL_DEVICE, desired_temp)

    except Exception as e:
        if logger:
            logger.error("Error communicating with pool controller: %s", e)
        else:
            print("Error communicating with ScreenLogic:", e)
    finally:
        await gateway.async_disconnect()


# --------------------------------------------------------------------------------
def test_spa_on_off(
    ip: str = GATEWAY_IP, disp_msg: bool = False, logger: logging.Logger | None = None
) -> None:
    """
    Test various functions and show how the calls should take place

    Inputs:
        ip - str - the IP address of the pool controller
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:

    """

    result_values, result_keys = asyncio.run(read_screenlogic(ip, disp_msg=disp_msg))
    pprint.pprint(result_values)
    # asyncio.run(set_heat_mode_spa(ip, 1, disp_msg=disp_msg))
    asyncio.run(set_spa_temp(ip, 90, disp_msg=disp_msg))
    result_values, result_keys = asyncio.run(read_screenlogic(ip, disp_msg=disp_msg))
    pprint.pprint(result_values)
    if False:
        asyncio.run(set_heat_mode_spa(ip, 0, disp_msg=disp_msg))
        result_values, result_keys = asyncio.run(
            read_screenlogic(ip, disp_msg=disp_msg)
        )
        pprint.pprint(result_values)


def main(
    ip: str = GATEWAY_IP, disp_msg: bool = False, logger: logging.Logger | None = None
) -> tuple[list, list]:
    """
    get the current settings for the passed in device

    Inputs:
        ip - str - the IP address of the pool controller
        disp_msg - bool - when true, we print out statements to show what is going on
        logger - logging - when populated - we log messages to the log file

    Returns:
        result_values - list - of result values
        result_keys - list - of the keys to those values

    """

    result_keys, result_values = asyncio.run(
        read_screenlogic(ip, disp_msg=disp_msg, logger=logger)
    )
    return result_values, result_keys


if __name__ == "__main__":
    if True:
        test_spa_on_off(disp_msg=True)
    if False:
        result_values, result_keys = main(disp_msg=True)
        if DEBUG:
            print(result_values, "\n", result_keys)


# eof
