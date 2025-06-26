@echo off

@REM add the envvar.bat file to move below variable to that file. 
@REM variable are set here
set id=
set validateMain1RUN=
set nmap=
SET F=%~dp0

@REM this will import your path variable file. 
call %~dp0\pathVariable.bat



@REM check if parameter where pass with bat file
if [%1] == [] Goto usageMessage1

@REM Remind user to get main.js file before proceeding 
echo --------------------------------------------------------------------------------------
echo ^|    Reminder: Download main.js and save to the same directory of webscan script    ^|
echo --------------------------------------------------------------------------------------

@REM This is just the welcome message and check for the port and if there is none it will set it up to 443. 
echo ---------------------------------------------
echo ^|    Do you wanna scan all the ports.       ^|
echo ---------------------------------------------

IF [%2] == [] (
  SET PORT=443
) ELSE (
  SET PORT=%2
)

@REM This code will ask the user for input to determine where to go. 
:Questions
echo Yes = 1
echo No = 2
echo Exit = 0
set /p id=:
if [%id%] == [] Goto usageMessage2
if [%id%] == [1] Goto addingAllPortsScript
if [%id%] == [2] Goto mainNmapsScript 
If [%id%] == [0] Goto exitRunningScript

@REM This is the message when parameter 0 in selected
:exitRunningScript
echo ---------------------------------------------
echo ^|          Have a Great Day!!               ^|
echo ---------------------------------------------
exit /b

@REM This is the message when no domain is inserted
:usageMessage1
echo ----------------------------------------------------------
echo ^| Usage: web_server_scan.bat  (domain) (port_if_not_443) ^|
echo -----------------------------------------------------------
exit /b 

@REM This is the message when no option was selected
:usageMessage2
echo ---------------------------------------------
echo ^|Sorry you must select a option to continue.^|
echo ---------------------------------------------
@REM echo %1 and %port%
Goto questions

@rem This mainNmapsScript verify if the nmap variable is set to 1 to decide if it 
@rem move to the nmapWithoutAllPortsMain or nmapWithoutAllPortsScriptCode
:mainNmapsScript
if [%nmap%] == [1] (
  Goto nmapWithoutAllPortsMain 
) else (
  Goto nmapWithoutAllPortsScriptCode
)

@REM This if statement verify if the variable id is set to 1 to set the next two variable and continue with all port scan. 
:nmapWithoutAllPortsMain
if [%id%] == [1] (
    set nmap=1
    set validateMain1RUN=4
    Goto addingAllPortsScript
) Else (
    Goto otherScriptCodes
)

exit /b 

@rem This if statement verify if the variable nmap is set to 1 at nmapWithoutAllPortsMain to determine 
@rem if it move to nmapWithAllPortsMain or nmapWithAllPortsScriptCode
:addingAllPortsScript
if [%nmap%] == [1] (
  Goto nmapWithAllPortsMain 
) else (
  Goto nmapWithAllPortsScriptCode
)

@REM This if statement check for validateMain1RUN variable to check if is set to 4 to either
@REM determine to go to the other scripts or go to mainNmapsScript
:nmapWithAllPortsMain
if [%validateMain1RUN%] == [4] (  
  Goto otherScriptCodes
) Else Goto mainNmapsScript

exit /b 

@REM This Goto label is to print and finidh the script

:End
echo ---------------------------------------------
echo ^|        Finished with the script!          ^|
echo ---------------------------------------------
exit /b

@REM This section/Goto label is where the nmap code will be added at the echo line all the code. 
:nmapWithoutAllPortsScriptCode

rem echo Starting NMap Web Server scan
rem echo ---------------------------------------------
rem echo ^|      Starting NMap Web Server scan       ^|
rem echo ---------------------------------------------
rem echo %NMAPPATH% -sC -sV -oX %1-nmap-web-server.xml --stylesheet="nmap.xsl" %1
rem call %NMAPPATH% -sC -sV -oX %1-nmap-web-server.xml --stylesheet=%XSLPATH% %1

rem echo ---------------------------------------------
rem echo ^|      Starting Xalan.jar XML to HDML      ^|
rem echo ---------------------------------------------
rem echo java -jar xalan.jar -IN %1-nmap-web-server.xml -OUT %1-nmap-web-server.html
rem call java -jar  %XALANPATH% -IN %1-nmap-web-server.xml -OUT %1-nmap-web-server.html

rem rem echo Starting NMap Web Header scan
rem echo ---------------------------------------------
rem echo ^|     Starting NMap Web Header scan       ^|
rem echo ---------------------------------------------
rem echo %NMAPPATH% -sV -sS -O -v1 --script=banner,http-headers -oX %1-nmap-web-header.xml --stylesheet="nmap.xsl" %1
rem call %NMAPPATH% -sV -sS -v1 -O --script=banner,http-headers -oX %1-nmap-web-header.xml --stylesheet=%XSLPATH% %1

rem echo ---------------------------------------------
rem echo ^|      Starting Xalan.jar XML to HDML      ^|
rem echo ---------------------------------------------
rem echo java -jar xalan.jar -IN %1-nmap-web-header.xml -OUT %1-nmap-web-header.html
rem call java -jar %XALANPATH% -IN %1-nmap-web-header.xml -OUT %1-nmap-web-header.html


::--------------------------NMap---------------------------------------------

echo ---------------------------------------------
echo ^|      Starting NMap Web Server scan new   ^|
echo ---------------------------------------------
echo %NMAPPATH% -sC -sV -O -v1 --script=banner,http-headers -oX %1-nmap-web-server.xml --stylesheet="nmap.xsl" %1
call %NMAPPATH% -sC -sV -O -v1 --script=banner,http-headers -oX %1-nmap-web-server.xml --stylesheet=%XSLPATH% %1

echo ---------------------------------------------
echo ^|      Starting Xalan.jar XML to HDML      ^|
echo ---------------------------------------------
echo java -jar xalan.jar -IN %1-nmap-web-server.xml -OUT %1-nmap-web-server.html
call java -jar  %XALANPATH% -IN %1-nmap-web-server.xml -OUT %1-nmap-web-server.html

echo ---------------------------------------------
echo ^|          Starting nmap SSL scan          ^|
echo ---------------------------------------------
echo %NMAPPATH% -v1 -p %port% --script=ssl-enum-ciphers -oX %1-nmap-ssl.xml --stylesheet="nmap.xsl" %1 
call %NMAPPATH% -v1 -p %port% --script=ssl-enum-ciphers -oX %1-nmap-ssl.xml --stylesheet=%XSLPATH% %1 

echo Starting Xalan.jar XML to HDML
echo ---------------------------------------------
echo ^|      Starting Xalan.jar XML to HDML      ^|
echo ---------------------------------------------
echo java -jar xalan.jar -IN %1-nmap-ssl.xml -OUT %1-nmap-ssl.html
call java -jar %XALANPATH% -IN %1-nmap-ssl.xml -OUT %1-nmap-ssl.html




::--echo ////////////////////////////////////////////// BOF - Replace Vulscan with Vulners script ///////////////////////////////////////////////////////
::--echo ---------------------------------------------
::--echo ^|        Starting NMap Vulscan scan        ^|
::--echo ---------------------------------------------
::--echo %NMAPPATH% -sV -sS -O -v1 --script=vulscan/vulscan.nse vulscandb=cve.csv -oX %1-nmap-vulscan.xml --stylesheet="nmap.xsl" %1
::--call %NMAPPATH% -sV -sS -O -v1 --script=vulscan/vulscan.nse vulscandb=cve.csv -oX %1-nmap-vulscan.xml --stylesheet=%XSLPATH% %1

::--echo %NMAPPATH% -sV -sS -O -v1 --script=vulscan/vulscan.nse vulscandb=cve.csv -oX %1-nmap-vulscan.xml --stylesheet="nmap.xsl" %1
::--call %NMAPPATH% -sV -sS -O -v1 --script=vulscan/vulscan.nse vulscandb=cve.csv -oX %1-nmap-vulscan.xml --stylesheet=%XSLPATH% %1
::-- nmap -sV -sS -O -v1 --script=vulscan/vulscan.nse --script-args vulscandb=cve.csv -oX scanme.nmap.org-nmap-vulscan.xml --stylesheet=C:\\Tools\\xalan-j_2_7_2\\nmap.xsl scanme.nmap.org
::-- java -jar C:\Tools\xalan-j_2_7_2\xalan.jar -IN scanme.nmap.org-nmap-vulscan.xml -OUT scanme.nmap.org-nmap-vulscan.html  

::--echo ---------------------------------------------
::--echo ^|      Starting Xalan.jar XML to HDML      ^|
::--echo ---------------------------------------------
::--echo java -jar xalan.jar -IN %1-nmap-vulscan.xml -OUT %1-nmap-vulscan.html
::--call java -jar %XALANPATH% -IN %1-nmap-vulscan.xml -OUT %1-nmap-vulscan.html


echo ---------------------------------------------
echo ^|        Starting NMap Vulners scan        ^|
echo ---------------------------------------------
echo %NMAPPATH% -sV -sS -O -v1 --script=vulners.nse -oX %1-nmap-vulners.xml --stylesheet="nmap.xsl" %1
call %NMAPPATH% -sV -sS -O -v1 --script=vulners.nse -oX %1-nmap-vulners.xml --stylesheet=%XSLPATH% %1

echo ---------------------------------------------
echo ^|      Starting Xalan.jar XML to HDML      ^|
echo ---------------------------------------------
echo java -jar xalan.jar -IN %1-nmap-vulners.xml -OUT %1-nmap-vulners.html
call java -jar %XALANPATH% -IN %1-nmap-vulners.xml -OUT %1-nmap-vulners.html

::--echo ////////////////////////////////////////////////// EOF - Replace Vulscan with Vulners script ///////////////////////////////////////////////////

goto nmapWithoutAllPortsMain

@REM This section/Goto label is where the nmap code will be added at the echo line all the code. 
:nmapWithAllPortsScriptCode

echo Starting NMap scan - extended ports
echo ---------------------------------------------
echo ^|    Starting NMap scan - extended ports   ^|
echo ---------------------------------------------
echo nmap -Pn -p- -vv -oX nmap-extended-ports-%1.xml --stylesheet="nmap.xsl"  %1
call nmap -Pn -p- -vv -oX nmap-extended-ports-%1.xml --stylesheet=%XSLPATH%  %1

echo ---------------------------------------------
echo ^|      Starting Xalan.jar XML to HDML      ^|
echo ---------------------------------------------
echo java -jar xalan.jar -IN nmap-extended-ports-%1.xml -OUT nmap-extended-ports-%1.html
call java -jar %XALANPATH% -IN nmap-extended-ports-%1.xml -OUT nmap-extended-ports-%1.html

goto nmapWithAllPortsMain

@REM This section/Goto label is where the rest of the code will be added under their respective name. 
:otherScriptCodes

::--------------------------sslscan--------------------------------------------

echo ---------------------------------------------
echo ^|             Starting SSLScan             ^|
echo ---------------------------------------------
echo sslscan --no-failed %1 > sslscan-%1.txt
call sslscan --no-failed %1 >> sslscan-%1.txt

::--------------------------sslyze---------------------------------------------

echo ---------------------------------------------
echo ^|      Starting SSLyze with Python 3       ^|
echo ---------------------------------------------
echo python -m sslyze --regular %1 > sslyze-%1.txt
call python -m sslyze --regular %1 >> sslyze-%1.txt


::--------------------------Heartbleed check---------------------------------------------
echo ---------------------------------------------
echo ^|        Starting NMap Heartbleed test    ^|
echo ---------------------------------------------
echo If vulnerable, you will see "State: VULNERABLE" in the scan results > nmap-ssl-heartbleed-%1.txt
echo ---------------------------------------------------------- >> nmap-ssl-heartbleed-%1.txt
echo %NMAPPATH% -p 443 --script ssl-heartbleed %1 >> nmap-ssl-heartbleed-%1.txt
call %NMAPPATH% -p 443 --script ssl-heartbleed %1 >> nmap-ssl-heartbleed-%1.txt


echo ---------------------------------------------
echo ^|        Starting ng-parser                ^|
echo ---------------------------------------------
echo This will fail if main.js is not found in the same folder as the scanning script
echo python %NGPARSER% main.js 
call python %NGPARSER% main.js

::--------------------------Subdomain check---------------------------------------------
echo ---------------------------------------------
echo ^|        Starting dig                     ^|
echo ---------------------------------------------
echo View all the record types (A, MX, NS, etc.) > dig-record-types-%1.txt
echo ------------------------------------------------------ >> dig-record-types-%1.txt
echo dig %1 -t any >> dig-record-types-%1.txt
call dig %1 -t any >> dig-record-types-%1.txt

echo Request to get a copy of the zone transfer from the primary server > dig-zone-transfer-%1.txt
echo (Transfer failed. means the application PASS the test) >> dig-zone-transfer-%1.txt
echo -----------------------------------------------------  >> dig-zone-transfer-%1.txt
echo dig %1 -t axfr >> dig-zone-transfer-%1.txt
call dig %1 -t axfr >> dig-zone-transfer-%1.txt


echo ---------------------------------------------
echo ^|    Starting crt script on domain.com    ^|
echo ---------------------------------------------
echo python %CRT% --domain %1 > crt-domain-%1.txt
call python %CRT% --domain %1 >> crt-domain-%1.txt

echo ---------------------------------------------
echo ^|  Starting crt script on sub.domain.com  ^|
echo ---------------------------------------------
echo %1 | findstr /c:"." > tempDomain.txt
for /f "tokens=2,3 delims=:." %%G in (tempDomain.txt) do set parentDomain=%%G.%%H
echo python %CRT% --domain %parentDomain% > crt-subdomain-%1.txt
call python %CRT% --domain %parentDomain% >> crt-subdomain-%1.txt


echo ---------------------------------------------
echo ^|        Starting NMap dns-brute script    ^|
echo ---------------------------------------------
echo Nmap brute force subdomain enumeration > nmap-DNS-brute-%1.txt
echo ------------------------------------------------------ >> nmap-DNS-brute-%1.txt
echo %NMAPPATH% --script dns-brute %1 >> nmap-DNS-brute-%1.txt
call %NMAPPATH% --script dns-brute %1 >> nmap-DNS-brute-%1.txt


::--------------------------nikto----------------------------------------------

echo Starting Nikto
echo ---------------------------------------------
echo ^|              Starting Nikto              ^|
echo ---------------------------------------------
echo nikto -C all -ssl %PORT% -Format HTML -output nikto-%1.html -Save niktosave -host %1
call nikto -C all -ssl %PORT% -Format HTML -output nikto-%1.html -Save niktosave -host %1

Goto End
