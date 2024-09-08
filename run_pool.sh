# File:  run_pool.sh
# Created:  2024-02-07;kv
# Version:  2024-09-07;kv - added in spa turn off file
#           2024-08-31;kv

# Move the execution folder
# Activate python in VENV
# Run the program to determine what is going on
cd ~/Documents/code/pool
. venv/bin/activate
screenlogicpy -i 192.168.8.141 > output.txt
python pool.py
# If a file is generated - run code to turn off the pool
if test -f pool_heater_off.lck; then
    screenlogicpy -i 192.168.8.141 set heat-mode pool 0
    rm pool_heater_off.lck
fi
# If a file is generated - run code to turn off the spa
if test -f spa_heater_off.lck; then
    screenlogicpy -i 192.168.8.141 set heat-mode spa 0
    rm spa_heater_off.lck
fi
# eof
