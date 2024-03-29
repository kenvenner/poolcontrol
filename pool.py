'''
@author:   Ken Venner
@contact:  ken@venerllc.com
@version:  1.02

Take the output from "screenlogic > output.txt" 
and parse that data and create append the output
to the output filename

'''
import os.path
import os
import logging
import re
from datetime import datetime
import kvutil
import kvgmailsendsimple


# Logging Setup
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename=os.path.splitext(kvutil.scriptinfo()['name'])[0]+'.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# application variables
optiondictconfig = {
    'AppVersion' : {
        'value': '1.02',
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
    'email_from' : {
        'value' : '210608thSt@gmail.com',
        'description' : 'who sends out the email about pool heater on',
    },
    'email_to' : {
        'value' : 'ken@vennerllc.com, mscribner@bcciconst.com, reservations@michelleleighvacationrentals.com',
#        'value' : 'ken@vennerllc.com',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'email_subject' : {
        'value' : 'Villa Carneros Pool Heater is ',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'email_body' : {
        'value' : 'We have just detected that the pool heater is ',
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'scopes' : {
        'value' : None,
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'file_token_json' : {
        'value' : None,
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
    'file_credentials_json' : {
        'value' : None,
        'description' : 'defines the name of the file that says we sent a message about pool heater being on',
    },
}

### GLOBAL VARIABLES AND CONVERSIONS ###

# set the time for the run
now = datetime.now()
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
    
    if os.path.isfile(optiondict['pool_heater_filename']):
        # if there is a lock file

        # and the pool heater is not ON message
        # that the pool heater turned off and remove the lock file
        if pool_settings['pool_heat_mode'] == 'Off':
            # send message that heater is off
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['email_from'],
                optiondict['email_to'],
                optiondict['email_subject']+'OFF',
                optiondict['email_body']+'OFF',
                optiondict['scopes'],
                optiondict['file_token_json'],
                optiondict['file_credentials_json']
            )

            # remove the lock file
            os.remove(optiondict['pool_heater_filename'])

            # log message
            logger.info('Pool heater off - sent message: %s and removed file: %s', msgid['id'], optiondict['pool_heater_filename'])
    else:

        # if there is NO lock file

        # and the pool heater is ON message
        # that the pool heater is now ON and create a lock file.
        if pool_settings['pool_heat_mode'] != 'Off':
            # send message that heater is ON
            msgid = kvgmailsendsimple.gmail_send_simple_message(
                optiondict['email_from'],
                optiondict['email_to'],
                optiondict['email_subject']+'ON',
                optiondict['email_body']+'ON',
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

    # determine if we need to message people
    message_on_pool_state_change(pool_settings, optiondict)
    

# eof

