@echo off
pushd %~dp0
set python_script=pegasus_update.py
start [path_to_env]\pythonw.exe %python_script%
popd
exit