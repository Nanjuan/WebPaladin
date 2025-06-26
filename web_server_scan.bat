@echo off
setlocal enabledelayedexpansion

REM WebPaladin - Windows Batch Script Version
REM Enhanced version with modular scanning options and dependency checking
REM
REM Author: Nestor Torres (@n3stortorres)
REM For questions or support, contact me on X (Twitter) @n3stortorres
REM or open an issue on GitHub.

REM Colors for output (Windows 10+ supports ANSI colors)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Global variables
set "DOMAIN="
set "PORT=443"
set "SCAN_DIR=scan_results"
set "TOOLS_DIR=tools"
set "TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%"

REM Function to print colored output
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Function to check if a command exists
:command_exists
where %~1 >nul 2>&1
if %errorlevel% equ 0 (
    set "exists=1"
) else (
    set "exists=0"
)
goto :eof

REM Function to detect OS
:detect_os
set "os=windows"
goto :eof

REM Function to install tools (Windows version)
:install_tool
call :print_status "Installing %~1..."
call :print_warning "Windows installation not automated. Please install %~1 manually."
call :print_status "You can install tools using:"
call :print_status "  - Chocolatey: choco install %~1"
call :print_status "  - Scoop: scoop install %~1"
call :print_status "  - Manual download from official websites"
set "install_success=0"
goto :eof

REM Function to check and install dependencies
:check_dependencies
call :print_status "Checking dependencies..."

set "missing_tools="
set "tools=nmap sslscan nikto python java"

for %%t in (%tools%) do (
    call :command_exists %%t
    if !exists! equ 0 (
        if defined missing_tools (
            set "missing_tools=!missing_tools! %%t"
        ) else (
            set "missing_tools=%%t"
        )
    ) else (
        call :print_success "%%t is installed"
    )
)

REM Check for sslyze specifically
python -c "import sslyze" >nul 2>&1
if %errorlevel% neq 0 (
    if defined missing_tools (
        set "missing_tools=!missing_tools! sslyze"
    ) else (
        set "missing_tools=sslyze"
    )
) else (
    call :print_success "sslyze is installed"
)

if not defined missing_tools (
    call :print_success "All dependencies are installed!"
    set "deps_ok=1"
    goto :eof
) else (
    call :print_warning "Missing tools: !missing_tools!"
    echo.
    set /p "install_choice=Would you like to install missing tools? (y/n): "
    if /i "!install_choice!"=="y" (
        for %%t in (!missing_tools!) do (
            echo.
            set /p "install_tool=Install %%t? (y/n): "
            if /i "!install_tool!"=="y" (
                call :install_tool %%t
            )
        )
    )
    set "deps_ok=0"
)
goto :eof

REM Function to setup scan directory
:setup_scan_directory
if not exist "%SCAN_DIR%" (
    mkdir "%SCAN_DIR%"
    call :print_success "Created scan directory: %SCAN_DIR%"
) else (
    call :print_status "Scan directory already exists: %SCAN_DIR%"
)
goto :eof

REM Function to run nmap web scan
:run_nmap_web_scan
call :print_status "Running Nmap web server scan..."
set "output_file=%SCAN_DIR%\nmap-web-scan-%TIMESTAMP%.xml"
nmap -sV -sC -p %PORT% --script=http-title,http-server-header,http-headers,http-enum,http-vuln* %DOMAIN% -oX "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "Nmap web scan completed: %output_file%"
    call :_convert_xml_to_html "%output_file%"
) else (
    call :print_error "Nmap web scan failed"
)
goto :eof

REM Function to run nmap SSL scan
:run_nmap_ssl_scan
call :print_status "Running Nmap SSL scan..."
set "output_file=%SCAN_DIR%\nmap-ssl-scan-%TIMESTAMP%.xml"
nmap -sV -sC -p %PORT% --script=ssl-cert,ssl-enum-ciphers,ssl-heartbleed,ssl-poodle,ssl-ccs-injection,ssl-known-key %DOMAIN% -oX "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "Nmap SSL scan completed: %output_file%"
    call :_convert_xml_to_html "%output_file%"
) else (
    call :print_error "Nmap SSL scan failed"
)
goto :eof

REM Function to run nmap vulners scan
:run_nmap_vulners_scan
call :print_status "Running Nmap vulners scan..."
set "output_file=%SCAN_DIR%\nmap-vulners-scan-%TIMESTAMP%.xml"
nmap -sV -sC -p %PORT% --script=vulners %DOMAIN% -oX "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "Nmap vulners scan completed: %output_file%"
    call :_convert_xml_to_html "%output_file%"
) else (
    call :print_error "Nmap vulners scan failed"
)
goto :eof

REM Function to run extended port scan
:run_extended_port_scan
call :print_status "Running extended port scan..."
set "output_file=%SCAN_DIR%\nmap-extended-scan-%TIMESTAMP%.xml"
nmap -sS -sV -sC -p- --min-rate=1000 %DOMAIN% -oX "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "Extended port scan completed: %output_file%"
    call :_convert_xml_to_html "%output_file%"
) else (
    call :print_error "Extended port scan failed"
)
goto :eof

REM Function to convert XML to HTML
:_convert_xml_to_html
set "xml_file=%~1"
set "html_file=%xml_file:.xml=.html%"

if exist "Nmap-reports-files\nmap.xsl" (
    call :print_status "Converting XML to HTML..."
    xsltproc "Nmap-reports-files\nmap.xsl" "%xml_file%" > "%html_file%"
    if %errorlevel% equ 0 (
        call :print_success "HTML report generated: %html_file%"
    ) else (
        call :print_warning "Failed to convert XML to HTML, creating simple report"
        call :_create_simple_html_report "%html_file%"
    )
) else (
    call :print_warning "Nmap XSL file not found, creating simple HTML report"
    call :_create_simple_html_report "%html_file%"
)
goto :eof

REM Function to create simple HTML report
:_create_simple_html_report
set "html_file=%~1"
set "xml_file=%html_file:.html=.xml%"

echo ^<!DOCTYPE html^> > "%html_file%"
echo ^<html^> >> "%html_file%"
echo ^<head^> >> "%html_file%"
echo     ^<title^>WebPaladin Scan Report^</title^> >> "%html_file%"
echo     ^<style^> >> "%html_file%"
echo         body { font-family: Arial, sans-serif; margin: 20px; } >> "%html_file%"
echo         .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; } >> "%html_file%"
echo         .content { margin-top: 20px; } >> "%html_file%"
echo         .section { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; } >> "%html_file%"
echo         .success { background-color: #d4edda; border-color: #c3e6cb; } >> "%html_file%"
echo         .warning { background-color: #fff3cd; border-color: #ffeaa7; } >> "%html_file%"
echo         .error { background-color: #f8d7da; border-color: #f5c6cb; } >> "%html_file%"
echo     ^</style^> >> "%html_file%"
echo ^</head^> >> "%html_file%"
echo ^<body^> >> "%html_file%"
echo     ^<div class="header"^> >> "%html_file%"
echo         ^<h1^>WebPaladin Security Scan Report^</h1^> >> "%html_file%"
echo         ^<p^>Target: %DOMAIN%:%PORT%^</p^> >> "%html_file%"
echo         ^<p^>Scan Date: %date% %time%^</p^> >> "%html_file%"
echo     ^</div^> >> "%html_file%"
echo     ^<div class="content"^> >> "%html_file%"
echo         ^<div class="section"^> >> "%html_file%"
echo             ^<h2^>Scan Information^</h2^> >> "%html_file%"
echo             ^<p^>This is a simple HTML report generated by WebPaladin.^</p^> >> "%html_file%"
echo             ^<p^>For detailed XML output, see: %xml_file%^</p^> >> "%html_file%"
echo         ^</div^> >> "%html_file%"
echo     ^</div^> >> "%html_file%"
echo ^</body^> >> "%html_file%"
echo ^</html^> >> "%html_file%"

call :print_success "Simple HTML report created: %html_file%"
goto :eof

REM Function to run sslscan
:run_sslscan
call :print_status "Running SSLScan..."
set "output_file=%SCAN_DIR%\sslscan-%TIMESTAMP%.txt"
sslscan --no-colour %DOMAIN%:%PORT% > "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "SSLScan completed: %output_file%"
) else (
    call :print_error "SSLScan failed"
)
goto :eof

REM Function to run sslyze
:run_sslyze
call :print_status "Running SSLyze..."
set "output_file=%SCAN_DIR%\sslyze-%TIMESTAMP%.txt"
python -m sslyze --regular %DOMAIN%:%PORT% > "%output_file%" 2>&1
if %errorlevel% equ 0 (
    call :print_success "SSLyze completed: %output_file%"
) else (
    call :print_error "SSLyze failed"
)
goto :eof

REM Function to run heartbleed test
:run_heartbleed_test
call :print_status "Running Heartbleed test..."
set "output_file=%SCAN_DIR%\heartbleed-%TIMESTAMP%.txt"
nmap -p %PORT% --script=ssl-heartbleed %DOMAIN% > "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "Heartbleed test completed: %output_file%"
) else (
    call :print_error "Heartbleed test failed"
)
goto :eof

REM Function to run DNS enumeration
:run_dns_enumeration
call :print_status "Running DNS enumeration..."
set "output_file=%SCAN_DIR%\dns-enum-%TIMESTAMP%.txt"

echo DNS Enumeration Results for %DOMAIN% > "%output_file%"
echo ========================================== >> "%output_file%"
echo. >> "%output_file%"

REM A record
echo A Record: >> "%output_file%"
nslookup %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

REM AAAA record
echo AAAA Record: >> "%output_file%"
nslookup -type=AAAA %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

REM MX record
echo MX Record: >> "%output_file%"
nslookup -type=MX %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

REM NS record
echo NS Record: >> "%output_file%"
nslookup -type=NS %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

REM TXT record
echo TXT Record: >> "%output_file%"
nslookup -type=TXT %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

REM SOA record
echo SOA Record: >> "%output_file%"
nslookup -type=SOA %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

REM CNAME record
echo CNAME Record: >> "%output_file%"
nslookup -type=CNAME %DOMAIN% >> "%output_file%" 2>&1
echo. >> "%output_file%"

call :print_success "DNS enumeration completed: %output_file%"
goto :eof

REM Function to run nikto
:run_nikto
call :print_status "Running Nikto web vulnerability scanner..."
set "output_file=%SCAN_DIR%\nikto-%TIMESTAMP%.txt"
nikto -h %DOMAIN% -p %PORT% -output "%output_file%"
if %errorlevel% equ 0 (
    call :print_success "Nikto scan completed: %output_file%"
) else (
    call :print_error "Nikto scan failed"
)
goto :eof

REM Function to show menu
:show_menu
echo.
echo ========================================
echo           WebPaladin Scanner
echo ========================================
echo.
echo Target: %DOMAIN%:%PORT%
echo.
echo Available scans:
echo 1. Nmap Web Server Scan
echo 2. Nmap SSL/TLS Scan
echo 3. Nmap Vulners Scan
echo 4. Extended Port Scan
echo 5. SSLScan
echo 6. SSLyze
echo 7. Heartbleed Test
echo 8. DNS Enumeration
echo 9. Nikto Web Vulnerability Scan
echo 10. All Scans
echo 11. Exit
echo.
goto :eof

REM Function to get user selection
:get_user_selection
set /p "choice=Enter your choice (1-11): "
goto :eof

REM Function to run selected scan
:run_selected_scan
set "scan_choice=%~1"

if "%scan_choice%"=="1" (
    call :run_nmap_web_scan
) else if "%scan_choice%"=="2" (
    call :run_nmap_ssl_scan
) else if "%scan_choice%"=="3" (
    call :run_nmap_vulners_scan
) else if "%scan_choice%"=="4" (
    call :run_extended_port_scan
) else if "%scan_choice%"=="5" (
    call :run_sslscan
) else if "%scan_choice%"=="6" (
    call :run_sslyze
) else if "%scan_choice%"=="7" (
    call :run_heartbleed_test
) else if "%scan_choice%"=="8" (
    call :run_dns_enumeration
) else if "%scan_choice%"=="9" (
    call :run_nikto
) else if "%scan_choice%"=="10" (
    call :print_status "Running all scans..."
    call :run_nmap_web_scan
    call :run_nmap_ssl_scan
    call :run_nmap_vulners_scan
    call :run_extended_port_scan
    call :run_sslscan
    call :run_sslyze
    call :run_heartbleed_test
    call :run_dns_enumeration
    call :run_nikto
    call :print_success "All scans completed!"
) else if "%scan_choice%"=="11" (
    call :print_status "Exiting..."
    exit /b 0
) else (
    call :print_error "Invalid choice. Please select 1-11."
)
goto :eof

REM Function to get domain and port
:get_domain_and_port
echo.
echo ========================================
echo           WebPaladin Scanner
echo ========================================
echo.
set /p "DOMAIN=Enter target domain/IP: "
if "%DOMAIN%"=="" (
    call :print_error "Domain cannot be empty"
    goto :get_domain_and_port
)

set /p "PORT=Enter port (default 443): "
if "%PORT%"=="" set "PORT=443"

call :print_status "Target set to: %DOMAIN%:%PORT%"
goto :eof

REM Main function
:main
echo.
echo %BLUE%========================================%NC%
echo %BLUE%           WebPaladin Scanner%NC%
echo %BLUE%========================================%NC%
echo.

REM Check dependencies
call :check_dependencies
if "%deps_ok%"=="0" (
    call :print_warning "Some dependencies are missing. Scans may fail."
    echo.
    set /p "continue_choice=Continue anyway? (y/n): "
    if /i not "!continue_choice!"=="y" (
        call :print_status "Exiting..."
        exit /b 1
    )
)

REM Setup scan directory
call :setup_scan_directory

REM Get domain and port
call :get_domain_and_port

REM Main loop
:main_loop
call :show_menu
call :get_user_selection
call :run_selected_scan "%choice%"
echo.
set /p "continue_choice=Run another scan? (y/n): "
if /i "!continue_choice!"=="y" (
    goto :main_loop
) else (
    call :print_status "Exiting..."
    exit /b 0
)

REM Entry point
:start
call :main
