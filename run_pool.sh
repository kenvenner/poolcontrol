# File:  run_pool.sh
# Created:  2024-02-07;kv
# Version:  2024-02-07;kv

# Move the execution folder
# Activate python in VENV
# Run the program
cd ~/Documents/code/pool
. venv/bin/activate
screenlogicpy -i 192.168.8.141 > output.txt
python pool.py
# eof
