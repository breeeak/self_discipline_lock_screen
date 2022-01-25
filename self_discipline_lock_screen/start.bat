@echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
D:
call D:\2_Develop\ANACONDA\Scripts\activate.bat  D:\2_Develop\ANACONDA\envs\LockScreen36
cd D:\3_Research\1_Project\1_Python\LockScreenTimer\self_discipline_lock_screen
start /b python main.py