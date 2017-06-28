goto EndOfLicense
# Copyright 2017 Lockheed Martin Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
:EndOfLicense

@echo off
SET iserr=0
SET SCRIPTDIR=%~dp0
SET DARTROOTDIR=%~dp0..\..\
SET DOWNLOADSDIR=%SCRIPTDIR%downloads\
SET REQUIREMENTSFILE=%~dp0..\..\requirements.txt 

REM DART Offline Installation
REM Copyright 2017 Lockheed Martin Corporation
REM Created: 2015-06-26
REM Version: 3.0 (2016-12-01)

echo DART Offline Installer (Windows 7)
echo Created by the Lockheed Martin Red Team
echo.
echo.

echo This will install the dependencies for DART.
echo.
pause

echo
echo [-] Checking for Admin privileges

REM UAC check/prompt from techgainer.com/create-batch-file-automatically-run-adminstrator

:: BatchGotAdmin (Run as Admin code starts)
REM Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
REM If error flag set, we do not have admin

if '%errorlevel%' NEQ '0' (
echo [!] Not running as admin
echo     This script requires administrative rights to run in order to:
echo         - Add Python to the system path
echo [-] Requesting admin privileges ^(will restart script as admin^)
pause
goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B

:gotAdmin
echo [-] Check passed - running as admin
if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
pushd "%CD%"
REM CD /D "%~dp0"

:: BatchGotAdmin (Run as Admin code ends)

echo [-] Beginning installation of vcpython27
msiexec /i %DOWNLOADSDIR%vcpython27.msi -qb
echo [-] vcpython27 installed

echo [-] Beginning installation of Python 2.7
msiexec /i %DOWNLOADSDIR%python-installer.msi /qb!
echo [-] Python 2.7 installed

echo [-] Adding Python to PATH
>nul 2>&1 SETX /M path "%PATH%;C:\Python27;C:\Python27\Scripts"
if '%errorlevel%' NEQ '0' (
echo [!] ERROR adding Python to path. Please manually add 
echo     C:\Python27 and C:\Python27\Scripts
echo     to your system path, then reboot.
SET iserr=1
) else (
echo [-] Added C:\Python27 and C:\Python27\Scripts to PATH
)

echo [-] Installing required components
C:\Python27\Scripts\pip.exe install --no-index --find-links=%DOWNLOADSDIR% -r %REQUIREMENTSFILE%
echo [-] Components installed.

echo.
echo.

if '%iserr%' NEQ '0' (
echo [!] SCRIPT ENCOUNTERED ERRORS
echo [!] Please review the output and take appropriate action.
echo.
echo.
)

echo [!] You should probably reboot this computer.
echo [!] You may encounter problems  
echo     if you do not reboot before running DART.

echo.
echo.
pause
