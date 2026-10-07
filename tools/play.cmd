@echo off
rem Crash 'n Burn on 3dokit's runtime, in a window (pfboot --window): the keyboard and a gamepad
rem as the pad, in real time. Keys: arrows; Z, X, C = A, B, C; Enter = P (start); Backspace = X
rem (stop); Q, W = L, R; closing the window ends the run. The presses are written to build\play-pad.txt as --pad options
rem that replay the run with pfboot; what pfboot says (and why a run stopped) to build\play-log.txt.
rem Extra arguments go to pfboot (say --pad a@1300x1).
setlocal
set PATH=C:\msys64\mingw64\bin;%PATH%
cd /d "%~dp0.."
echo Crash 'n Burn -- pfboot --window. The log goes to build\play-log.txt.
build\recomp-build\pfboot.exe build\disc\launchme --trace 0 --window --record build\play-pad.txt %* > build\play-log.txt 2>&1
echo pfboot ended with code %ERRORLEVEL%. Its last words:
powershell -NoProfile -Command "Get-Content build\play-log.txt -Tail 3"
pause
