# File:  run_pool.sh
# Created:  2024-02-07;kv
# Version:  2024-08-31;kv

# Move the execution folder
# Activate python in VENV
# Run the program to determine what is going on
# If a file is generated - run code to turn off the pool
cd ~/Documents/code/pool
. venv/bin/activate
screenlogicpy -i 192.168.8.141 > output.txt
python pool.py
if test -f pool_heater_off.lck; then
    screenlogicpy -i 192.168.8.141 set heat-mode pool 0
    rm pool_heater_off.lck
fi
# eof
