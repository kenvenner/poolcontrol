from __future__ import print_function

'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.02

Library of tools for date time processing used in general by KV

Update:  2024-06-06;kv - added try/except on datetime_from_str

'''

import os
import datetime
from dateutil import tz
from dateutil.zoneinfo import get_zonefile_instance
import sys
import errno

# setup the logger
import logging

logger = logging.getLogger(__name__)

# set the module version number
AppVersion = '1.02'
__version__ = '1.02'


def current_timezone_string():
    now = datetime.datetime.now()
    local_now = now.astimezone()
    local_tz = local_now.tzinfo
    local_tzname = local_tz.tzname(local_now)
    return local_tzname


def datetime2utcdatetime(dt, default_tz=None, no_tz=False):
    # define it because it was not passed in
    if default_tz is None:
        default_tz = tz.gettz()
    else:
        default_tz = tz.gettz(default_tz)

    # convert the naive date to localize date
    local_dt = dt.replace(tzinfo=default_tz)

    # convert the local time to UTC time
    utc_datetime = local_dt.astimezone(tz.UTC)

    # strip the timezone from datetime
    if no_tz:
        utc_datetime = utc_datetime.replace(tzinfo=None)

    return utc_datetime


# extract out a datetime value from a string if possible
# formats currently supported:
#  mm-dd-yy
#  mm-dd-yyyy
#  mm/dd/yy
#  mm/dd/yyyy
#  YYYY-MM-DDTHH:MM:SS
#  YYYY-MM-DDTHH:MM:SS.mmmmm
#  YYYY-MM-DD HH:MM:SS
#  YYYY-MM-DD HH:MM
#  YYYY-MM-DD
#  YYYYMMDD
#
# and allow a Z to be on the end of this string that we will strip out
#
def datetime_from_str(value, skipblank=False):
    import re
    datefmts = (
        (re.compile(r'\d{1,2}/\d{1,2}/\d{2}$'), '%m/%d/%y'),
        (re.compile(r'\d{1,2}/\d{1,2}/\d{4}$'), '%m/%d/%Y'),
        (re.compile(r'\d{1,2}-\d{1,2}-\d{2}$'), '%m-%d-%y'),
        (re.compile(r'\d{1,2}-\d{1,2}-\d{4}$'), '%m-%d-%Y'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}$'), '%Y-%m-%dT%H:%M:%S'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}\.\d+$'), '%Y-%m-%dT%H:%M:%S.%f'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}$'), '%Y-%m-%d %H:%M:%S'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}$'), '%Y-%m-%d %H:%M'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}$'), '%Y-%m-%d'),
        (re.compile(r'^\d{8}$'), '%Y%m%d'),
    )

    if skipblank and not value:
        return value

    orig_value = value
    
    # strip the Z on the end before processing
    if value[-1].upper() == 'Z':
        value = value[:-1]

    print('value:', value)

    for (redate, datefmt) in datefmts:
        if redate.match(value):
            try:
                return datetime.datetime.strptime(value, datefmt)
            except Exception as e:
                print('-'*40)
                print('datetime_from_str - conversion error:')
                print(f'    value..:  {value}')
                print(f'    datefmt:  {datefmt}')
                raise e
            
    raise Exception(u'Unable to convert to date time:{}'.format(orig_value))


# extract out a datetime value with timezone from a string if possible
# formats currently supported:
#     YYYY-MM-DD HH:MM:SS[+-]HHHH
#     YYYY-MM-DDTHH:MM:SS[+-]HHHH
#     YYYY-MM-DD HH:MM:SS.mmmm[+-]HHHH
#     YYYY-MM-DDTHH:MM:SS.mmmm[+-]HHHH
#
#     YYYY-MM-DD HH:MM:SS[+-]HH:HH
#     YYYY-MM-DDTHH:MM:SS[+-]HH:HH
#     YYYY-MM-DD HH:MM:SS.mmmm[+-]HH:HH
#     YYYY-MM-DDTHH:MM:SS.mmmm[+-]HH:HH
#
def datetimezone_from_str(value, skipblank=False):
    import re
    datefmtscleanup = (
        (re.compile(r'(.*[+-])(\d{2}):(\d{2})$'), 'remove-colon-2'),
    )
    datefmts = (
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}\.\d+[+-]\d{4}$'), '%Y-%m-%dT%H:%M:%S.%f%z'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\.\d+[+-]\d{4}$'), '%Y-%m-%d %H:%M:%S.%f%z'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}[+-]\d{4}$'), '%Y-%m-%dT%H:%M:%S%z'),
        (re.compile(r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}[+-]\d{4}$'), '%Y-%m-%d %H:%M:%S%z'),
    )

    if skipblank and not value:
        return value

    # see if we need to change the format of the data we got in
    for (redate, action) in datefmtscleanup:
        if redate.match(value):
            m = redate.match(value)
            if action == 'remove-colon-2':
                value = m.group(1) + m.group(2) + m.group(3)

    # convert date into date/time/zone
    for (redate, datefmt) in datefmts:
        if redate.match(value):
            return datetime.datetime.strptime(value, datefmt)

    # error out because we could not convert
    raise Exception(u'Unable to convert to date time:{}'.format(value))


def valid_tz_string(tzstr):
    if tz.gettz(tzstr):
        return True
    return False


def show_timezones(sublist=None, debug=False):
    # get the full list
    sorted_zonenames = sorted(list(get_zonefile_instance().zones))
    sections = set([x.split('/')[0] for x in sorted_zonenames if '/' in x])

    if sublist.capitalize() in sections:
        display_zonenames = [x for x in sorted_zonenames if x.startswith(str(sublist.capitalize()) + '/')]
    elif sublist.upper() in ('US', 'USA'):
        display_zonenames = [x for x in sorted_zonenames if x.startswith('US/')]
    elif sublist.upper() in ('SHORT', 'ABBR'):
        display_zonenames = [x for x in sorted_zonenames if '/' not in x]
    else:
        display_zonenames = sorted_zonenames

    print('Timezone Names:')
    for tzname in display_zonenames:
        print(tzname)

    return display_zonenames


# eof
