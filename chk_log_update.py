'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.01

Check the directory where log files are saved to validate they are 
updated within the window we expect - check the age of the 
log files we are checking and make sure the last modified date/time 
is no older than the specified number of seconds


'''
import os.path
import os
import logging
import re
import datetime
import kvutil
import kvgmailsendsimple
import pprint

# CONSTANTS
DAY_SECONDS = 60 * 60 * 24
FIFTEEN_MIN_SECONDS = 60 * 15
FOUR_HOUR_SECONDS = 60 * 60 * 4
EIGHT_HOUR_SECONDS = 2 * FOUR_HOUR_SECONDS
if False:
    FOUR_HOUR_SECONDS = 5
    EIGHT_HOUR_SECONDS = 5 * 60



def modification_date(filename):
    '''
    return the last modified date on a file in datetime format
    '''
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def modification_days_and_seconds(filename):
    '''
    return an array that has the (days, seconds) of the file modification date
    '''
    file_datetime = modification_date(filename)
    file_duration = datetime.datetime.now() - file_datetime
    return divmod(file_duration.total_seconds(), DAY_SECONDS)

               
# Logging Setup
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename=os.path.splitext(kvutil.scriptinfo()['name'])[0]+'.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# application variables
optiondictconfig = {
    'AppVersion' : {
        'value': '1.04',
        'description' : 'defines the version number for the app',
    },
    'debug' : {
        'value' : False,
        'type'  : 'bool',
        'description' : 'defines if we are running in debug mode',
    },
    'verbose' : {
        'value' : 1,
        'type'  : 'int',
        'description' : 'defines the display level for print messages',
    },
    'conf_json' : {
        'value' : None,
        'description' : 'defines the json configuration file to be read',
    },
    'check_files': {
        'value': [
            {
                'fname': 'G:/My Drive/VillaRaspi/pool_temps.csv',
                'max_age_seconds': FOUR_HOUR_SECONDS,
                'lock_fname': 'pool_temps.lck',
                'max_lock_age_seconds': EIGHT_HOUR_SECONDS
            },
            {
                'fname': 'G:/My Drive/VillaRaspi/villatemps.txt',
                'max_age_seconds': FOUR_HOUR_SECONDS,
                'lock_fname': 'villatemps.lck',
                'max_lock_age_seconds': EIGHT_HOUR_SECONDS
            },
        ],
        'type': 'list',
        'description': 'list of file records that we will process',
    },
    'email_from' : {
        'value' : '210608thSt@gmail.com',
        'description' : 'who sends out the email about pool heater on',
    },
    'email_to' : {
        'value' : 'ken@vennerllc.com',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'email_subject' : {
        'value' : 'Villa Carneros file check ',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'email_body' : {
        'value' : 'Checking for file ',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'scopes' : {
        'value' : None,
        'description' : 'defines the gmail scopes used to generate and send emails - see kvgmailsendsimple.py',
    },
    'file_token_json' : {
        'value' : None,
        'description' : 'defines the gmail filename of the json file that contains the account token (access and refresh) ',
    },
    'file_credentials_json' : {
        'value' : None,
        'description' : 'defines the gmail filename of the json file that contains the account credentials ',
    },
}

### GLOBAL VARIABLES AND CONVERSIONS ###

# set the time for the run
now = datetime.datetime.now()
now_str = now.strftime('%Y-%m-%d:%H:%M:%S')



def check_file_writable(fnm):
    if os.path.exists(fnm):
        # path exists
        if os.path.isfile(fnm): # is it a file or a dir?
            # also works when file is a link and the target is writable
            return os.access(fnm, os.W_OK)
        else:
            return False # path is a dir, so cannot write as a file
    # return False - file is not there
    return False

    # target does not exist, check perms on parent dir
    pdir = os.path.dirname(fnm)
    if not pdir: pdir = '.'
    # target is creatable if parent dir is writable
    return os.access(pdir, os.W_OK)


def message_on_file_too_old(fname, max_age_seconds, lock_fname, max_lock_age_seconds, optiondict):
    ''' 
    check to see if we have notified on aging file - by checking for lock file
        if lock file exists, check its age and see if it has exceeded its age
        if it has not exceed its age, return with no action

    get the current time since the file of interest was last modified
    compare to the max_age_seconds and 
    if the age is less - return

    send out a message using the dictionary msg_dict witih keys:
        email_from, email_to, email_subject, email_body
    and values from optiondict:
        scopes, file_token_json, file_credentials_json
    create a new/updated lock file
    '''

    msgid = None

    # LOCK FILE
    if lock_fname and os.path.isfile(lock_fname):
        # if there is a lock file - capture the informatoin about this lock file
        lock_days, lock_seconds = modification_days_and_seconds(lock_fname)

        # log message
        # logger.info('Lock file age %s is not older than %s', lock_seconds, max_lock_age_seconds)

        # check age of the lock file
        if lock_seconds < max_lock_age_seconds:
            return

    # Get the age of the file of interest
    if not os.path.isfile(fname):
        # send message that file does not exist
        msgid = kvgmailsendsimple.gmail_send_simple_message(
            optiondict['email_from'],
            optiondict['email_to'],
            optiondict['email_subject']+fname+'-does not exist',
            optiondict['email_body']+fname+'-does not exist',
            optiondict['scopes'],
            optiondict['file_token_json'],
            optiondict['file_credentials_json']
        )

        # create the lock file
        with open(lock_fname, 'w') as lock_file:
            lock_file.write('file does not exist')
            
        # log message
        logger.info('File is missing - sent message: %s and created file: %s', msgid['id'], fname)

        # done - so return
        return
    
    # if there is a lock file - capture the informatoin about this lock file
    fname_days, fname_seconds = modification_days_and_seconds(fname)

    # check age of the lock file
    if fname_seconds < max_age_seconds:
        return

    # we have aged out on the file and we have aged out on the last message sent
    # send message that file does not exist
    msgid = kvgmailsendsimple.gmail_send_simple_message(
        optiondict['email_from'],
        optiondict['email_to'],
        optiondict['email_subject']+fname+'-got stale',
        optiondict['email_body']+fname+'-got stale',
        optiondict['scopes'],
        optiondict['file_token_json'],
        optiondict['file_credentials_json']
    )

    # create the lock file
    with open(lock_fname, 'w') as lock_file:
        lock_file.write('file does not exist')
        
    # log message
    logger.info('File and lock are too old - sent message: %s and created file: %s', msgid['id'], fname)

    # return back the message id or none
    return msgid
    
    
# ---------------------------------------------------------------------------
if __name__ == '__main__':

    # capture the command line
    optiondict = kvutil.kv_parse_command_line( optiondictconfig, debug=False )

    # set variables based on what came form command line
    debug = optiondict['debug']

    # print header to show what is going on (convert this to a kvutil function:  kvutil.loggingStart(logger,optiondict))
    kvutil.loggingAppStart( logger, optiondict, kvutil.scriptinfo()['name'] )


    # step through each of the files to process
    for rec in optiondict['check_files']:
        message_on_file_too_old(rec['fname'], rec['max_age_seconds'], rec['lock_fname'], rec['max_lock_age_seconds'], optiondict)
    
    

# eof

