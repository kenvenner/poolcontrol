rem @echo off
echo %date% %time%
python -m screenlogicpy -i 192.168.8.141 > output.txt
python pool.py

