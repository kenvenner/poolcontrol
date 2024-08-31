rem @echo off
echo %date% %time%
python -m screenlogicpy -i 192.168.8.141 > output.txt
python pool.py
if not EXIST "pool_heater_off.lck" GOTO end
python -m screenlogicpy -i 192.168.8.141 set heat-mode pool 0
del pool_heater_off.lck
:end
