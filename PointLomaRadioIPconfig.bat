

set varip=10.0.42.55
set varsm=255.255.255.0
set vargw=10.0.42.1
set vardns1=
set vardns2=
set varhome=www.google.com


ECHO Setting IP Address and Subnet Mask
netsh int ip set address name = "Motherboard LAN" source = static addr = %varip% mask = %varsm%

ECHO Setting Gateway
netsh int ip set address name = "Motherboard LAN" gateway = %vargw% gwmetric = 1

ECHO Setting Primary DNS
netsh int ip set dns name = "Motherboard LAN" source = static addr = %vardns1%

ECHO Setting Secondary DNS
netsh int ip add dns name = "Motherboard LAN" addr = %vardns2%

ECHO Setting Internet Explorer Homepage to %varhome%
reg add "hkcu\software\microsoft\internet explorer\main" /v "Start Page" /d "%varhome%" /f

rem ECHO Here are the new settings for %computername%:
rem netsh int ip show config

pause