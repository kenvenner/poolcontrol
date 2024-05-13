'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.04

Take the output from "screenlogic > output.txt" 
and parse that data and create append the output
to the output filename

'''
import os.path
import os
import logging
import re
import datetime
import kvutil
import kvgmailsendsimple

# CONSTANTS
DAY_SECONDS = 60 * 60 * 24
FIFTEEN_MIN_SECONDS = 60 * 15



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
        'value' : ['pool.json'],
        'description' : 'defines the json configuration file to be read',
    },
    'input_filename' : {
        'value' : 'output.txt',
        'description' : 'defines the name of the file generated from screenlogic',
    },
    'pool_filename' : {
        'value' : 'pool_temps.csv',
        'description' : 'defines the name of the file that holds the temperature readings',
    },
    'pool_heater_filename' : {
        'value' : 'pool_heater.lck',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'pool_email_from' : {
        'value' : '210608thSt@gmail.com',
        'description' : 'who sends out the email about pool heater on',
    },
    'pool_email_to' : {
        'value' : 'ken@vennerllc.com, mscribner@bcciconst.com, reservations@michelleleighvacationrentals.com',
#        'value' : 'ken@vennerllc.com',  # uncomment for testing purposes
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'pool_email_subject' : {
        'value' : 'Villa Carneros Pool Heater is ',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'pool_email_body' : {
        'value' : 'We have just detected that the pool heater is ',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'spa_heater_filename' : {
        'value' : 'spa_heater.lck',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'spa_email_from' : {
        'value' : '210608thSt@gmail.com',
        'description' : 'who sends out the email about spa heater on',
    },
    'spa_email_to' : {
        'value' : 'ken@vennerllc.com',
        'description' : 'defines the name of the file that says we sent a message about spa heater being on',
    },
    'spa_email_subject' : {
        'value' : 'Villa Carneros SPA Heater is ',
        'description' : 'defines the name of the file that says we sent a message about spa heater being on',
    },
    'spa_email_body' : {
        'value' : 'We have just detected that the spa heater is ',
        'description' : 'defines the name of the file that says we sent a message about spa heater being on',
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


def read_parse_output_pool(input_file, output_file):

    # Using readlines()
    file1 = open(input_file, 'r')
    Lines = file1.readlines()

    # logging
    logger.info('Read in pool data from:  %s', input_file)
    logger.info('Lines in this file:  %d', len(Lines))

    # if the lines is not greater than 20 we did not get valid run
    if len(Lines) < 20:
        logger.info('Insufficient lines created - unable to parse file - EXITTING')
        return
    
    # Debugging
    # print(Lines)
    
    # count on lines
    count = 0
    
    # Strips the newline character
    for line in Lines:
        count += 1

        # debugging
        # print("Line{}: {}".format(count, line.strip()))

        m = re.search('Pool temperature is last\s+(\d+)', line)
        
        # print( count, m, line )
        if m:
            pool_temp_last = m.group(1)
            # print( pool_temp_last  )
            
            
        m = re.search('Pool Heat Set Point:\s+(\d+)', line)

        # print( count, m, line )
        if m:
            pool_temp_set = m.group(1)
            # print( pool_temp_set )

        m = re.search('Pool Heat:\s+(.+)', line)

        # print( count, m, line )
        if m:
            pool_heat_set = m.group(1)
            # print( pool_heat_set )


        m = re.search('Pool Heat Mode:\s+(.+)', line)

        # print( count, m, line )
        if m:
            pool_heat_mode = m.group(1)
            # print( pool_heat_mode)


        m = re.search('Spa temperature is last\s+(\d+)', line)

        # print( count, m, line )
        if m:
            spa_temp_last = m.group(1)
            # print( spa_temp_last )


        m = re.search('Spa Heat Set Point:\s+(\d+)', line)

        # print( count, m, line )
        if m:
            spa_temp_set = m.group(1)
            # print( spa_temp_set )

        m = re.search('Spa Heat:\s+(.+)', line)

        # print( count, m, line )
        if m:
            spa_heat_set = m.group(1)
            # print( spa_heat_set )
        

        m = re.search('Spa Heat Mode:\s+(.+)', line)

        # print( count, m, line )
        if m:
            spa_heat_mode = m.group(1)
            # print( spa_heat_mode )

    # append results
    file_writeable = check_file_writable( output_file )


    # debugging
    # print('file_writeable: ', file_writeable)
    
    
    # open file for output
    with open(output_file, "a") as file1:
        # create header if file does not exist
        if not file_writeable:
            # write header if it doe snot exist
            file1.write(','.join(['now_str',
                                  'pool_temp_last','pool_temp_set','pool_heat_set','pool_heat_mode',
                                  'spa_temp_last','spa_temp_set','spa_heat_set','spa_heat_mode'])
                        +'\n')
        
        # Writing data to a file
        file1.write(','.join([now_str,
                              pool_temp_last, pool_temp_set, pool_heat_set, pool_heat_mode,
                              spa_temp_last, spa_temp_set, spa_heat_set, spa_heat_mode])
                    +'\n')

        # logging
        logger.info('Appended record to: %s ', output_file)
        

        # remove the file if it exists
        if os.path.isfile(input_file):
            # remove the file
            os.remove(input_file)
            # logging
            logger.info('Removed input file:  %s', input_file)

    # return what we just read in
    return {
        'pool_temp_last': pool_temp_last,
        'pool_temp_set': pool_temp_set,
        'pool_heat_set': pool_heat_set,
        'pool_heat_mode': pool_heat_mode,
        'spa_temp_last': spa_temp_last,
        'spa_temp_set': spa_temp_set,
        'spa_heat_set': spa_heat_set,
        'spa_heat_mode': spa_heat_mode
    }


def message_on_pool_state_change(pool_settings, optiondict):
    ''' create an email when the state changes on pool heater
    using a lock file to capture what the state currently is

    pool_settings - dict of values read in 
    optiondict - the options dictionary

    '''

    msgid = None

    # POOL
    if os.path.isfile(optiondict['pool_heater_filename']):
        # if there is a lock file - capture the informatoin about this lock file
        pool_days, pool_seconds = modification_days_and_seconds(optiondict['pool_heater_filename'])        

        # and the pool heater is not ON message
        # that the pool heater turned off and remove the lock file
        if pool_settings['pool_heat_mode'] == 'Off':
            # send message that heater is off
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['pool_email_from'],
                optiondict['pool_email_to'],
                optiondict['pool_email_subject']+'OFF',
                optiondict['pool_email_body']+'OFF',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # remove the lock file
            os.remove(optiondict['pool_heater_filename'])

            # log message
            logger.info('Pool heater off - sent message: %s and removed file: %s', msgid['id'], optiondict['pool_heater_filename'])

        elif pool_days and pool_seconds < FIFTEEN_MIN_SECONDS:
            # we have a lock file and we have had this lock file exist for more than a day
            # we are greater than a day and less then the first 15 minutes of that next day
            # we should send another message about the duratoin of this being on
            # send message that heater is off
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['pool_email_from'],
                optiondict['pool_email_to'],
                optiondict['pool_email_subject']+'STILL ON - DAY ' + str(pool_days),
                'Pool Heater continues to be on',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # log message
            logger.info('Pool heater still ON [%s] days - sent message: %s and removed file: %s',
                        pool_days, msgid['id'], optiondict['pool_heater_filename'])

    else:

        # if there is NO lock file

        # and the pool heater is ON message
        # that the pool heater is now ON and create a lock file.
        if pool_settings['pool_heat_mode'] != 'Off':
            # send message that heater is ON
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['pool_email_from'],
                optiondict['pool_email_to'],
                optiondict['pool_email_subject']+'ON',
                optiondict['pool_email_body']+'ON',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # create the lock file
            with open(optiondict['pool_heater_filename'], 'w') as lock_file:
                lock_file.write('Pool ON')

            # log message
            logger.info('Pool heater ON - sent message: %s and created file: %s', msgid['id'], optiondict['pool_heater_filename'])


    # return back the message id or none
    return msgid
    
def message_on_spa_state_change(pool_settings, optiondict):
    ''' create an email when the state changes on spa heater
    using a lock file to capture what the state currently is

    pool_settings - dict of values read in 
    optiondict - the options dictionary

    '''

    msgid = None

    # SPA
    if os.path.isfile(optiondict['spa_heater_filename']):
        # if there is a lock file - capture the informatoin about this lock file
        spa_days, spa_seconds = modification_days_and_seconds(optiondict['pool_heater_filename'])
        
        # and the spa heater is not ON message
        # that the spa heater turned off and remove the lock file
        if pool_settings['spa_heat_mode'] == 'Off':
            # send message that heater is off
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['spa_email_from'],
                optiondict['spa_email_to'],
                optiondict['spa_email_subject']+'OFF',
                optiondict['spa_email_body']+'OFF',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # remove the lock file
            os.remove(optiondict['spa_heater_filename'])

            # log message
            logger.info('SPA heater off - sent message: %s and removed file: %s', msgid['id'], optiondict['spa_heater_filename'])

        elif spa_days and spa_seconds < FIFTEEN_MIN_SECONDS:
            # we have a lock file and we have had this lock file exist for more than a day
            # we are greater than a day and less then the first 15 minutes of that next day
            # we should send another message about the duratoin of this being on
            # send message that heater is off
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['spa_email_from'],
                optiondict['spa_email_to'],
                optiondict['spa_email_subject']+'STILL ON - DAY ' + str(spa_days),
                'SPA Heater continues to be on',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # log message
            logger.info('SPA heater still ON [%s] days - sent message: %s and removed file: %s',
                        spa_days, msgid['id'], optiondict['spa_heater_filename'])
            
    else:

        # if there is NO lock file

        # and the spa heater is ON message
        # that the spa heater is now ON and create a lock file.
        if pool_settings['spa_heat_mode'] != 'Off':
            # send message that heater is ON
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['spa_email_from'],
                optiondict['spa_email_to'],
                optiondict['spa_email_subject']+'ON',
                optiondict['spa_email_body']+'ON',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # create the lock file
            with open(optiondict['spa_heater_filename'], 'w') as lock_file:
                lock_file.write('SPA ON')

            # log message
            logger.info('SPA heater ON - sent message: %s and created file: %s', msgid['id'], optiondict['spa_heater_filename'])


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

        
    # process the pool file
    logger.info( "Call read and save pool data function" )
    pool_settings = read_parse_output_pool(optiondict['input_filename'], optiondict['pool_filename'])

    # POOL - determine if we need to message people
    message_on_pool_state_change(pool_settings, optiondict)
    
    # SPA determine if we need to message people
    message_on_spa_state_change(pool_settings, optiondict)
    

# eof

