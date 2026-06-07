@echo off
title PasswordGenerator Launcher
color 0B
mode con: cols=90 lines=25

cls
echo.------------------------------------------------------------------------------
echo.
echo                      PASSWORD GENERATOR BY K B Srivastava
echo.
echo ------------------------------------------------------------------------------
echo.
echo Password Generator is a Tkinter-based desktop password manager that
echo allows users to generate secure passwords, store encrypted credentials,
echo and maintain encrypted password history.
echo.
echo It combines PBKDF2-HMAC-SHA256 key derivation, Fernet encryption,
echo and a modern dark-themed interface to provide a secure and
echo user-friendly local password management solution.
echo.
echo -----------------------------------------------------------------
echo.
echo Encryption : PBKDF2-HMAC-SHA256 + Fernet
echo Storage    : Local Encrypted Vaults
echo Interface  : Modern Dark Theme (Tkinter)
echo Security   : Cryptographically Secure Password Generation
echo.
echo -----------------------------------------------------------------
echo.
echo Press ENTER to launch PasswordGuard...
echo.

set /p dummy=

cls
echo.
echo Initializing environment...
timeout /t 1 >nul
echo Checking Python installation...
timeout /t 1 >nul
echo Launching main application...
timeout /t 1 >nul
echo Intallation of Dependencies...
pip install -r requirements.txt
timeout /t 1 >nul

cd /d "%~dp0"

python main.py

echo.
echo Application closed.
timeout /t 2 >nul
exit
