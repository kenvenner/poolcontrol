import kvutil

import pool

import unittest

import time
import copy
import os

from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR

# create a filename
filename = kvutil.filename_unique( { 'base_filename' : 't_pooltest', 'file_ext' : '.txt', 'uniqtype' : 'datecnt', 'overwrite' : True, 'forceuniq' : True } )

# make file read-only
def file_read_only(filename):
    return os.chmod(filename, S_IREAD|S_IRGRP|S_IROTH)
def file_read_write(filename):
    return os.chmod(filename, S_IWUSR|S_IREAD)


# Testing class
class TestKVpool(unittest.TestCase):
    # executed on each test
    def setUp(self):
        kvutil.remove_filename(filename,kvutil.functionName(2), debug=False)

    def tearDown(self):
        kvutil.remove_filename(filename,kvutil.functionName(2), debug=False)

        
    # executed at the end of all tests - cleans up the environment
    @classmethod
    def tearDownClass(cls):
        kvutil.remove_filename(filename,kvutil.functionName(), debug=False)

    @classmethod
    def setUpClass(cls):
        kvutil.remove_filename(filename,kvutil.functionName(), debug=False)

    #def modification_date(filename):
    #def test_modification_date_p01_work(self):
        
    #def modification_days_and_seconds(filename):
    #def test_modification_days_and_seconds(self):

    #def check_file_writable(fnm):
    def test_check_file_writable_p01_simple(self):
        with open(filename, "w") as file1:
            file1.write('create read write file')
        self.assertTrue( pool.check_file_writable(filename), 'Writeable file not created: ' + filename )
    def test_check_file_writable_f01_read_only(self):
        with open(filename, "w") as file1:
            file1.write('create read only file')
        file_read_only(filename)
        self.assertFalse( pool.check_file_writable(filename), 'Writeable file not created: ' + filename )
        file_read_write(filename)
    def test_check_file_writable_f02_no_file(self):
        self.assertFalse( pool.check_file_writable('file_not_exist.txt'), 'Writeable file not created: ' + 'file_not_exist.txt' )
    def test_check_file_writable_f03_directory(self):
        self.assertFalse( pool.check_file_writable('.'), 'Writeable file not created: ' + '.' )

        

#def read_parse_output_pool(input_file, output_file):
#def message_on_pool_state_change(pool_settings, optiondict):
#def message_on_pool_turn_off(pool_settings, optiondict):
#def message_on_spa_state_change(pool_settings, optiondict):    

if __name__ == '__main__':
    unittest.main()
