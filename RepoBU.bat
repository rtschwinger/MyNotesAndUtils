svnadmin load --parent-dir F:\ProjectRepos\Projects\trunk\ F:\ProjectRepos\SolarWorld < F:ProjectRepos\solarworld.dmp


svnadmin hotcopy F:\ProjectRepos\SolarWorld F:\ProjectRepos\Projects\trunk\SolarWorld 



@ECHO OFF
REM    will hotcopy your repo to My Documents
REM    this will delete the existing dir and create it again
REM    you could use this script with a scheduled task for backup
REM    created by Jim Priest
REM    last edited 3:38 PM 8/14/2006

SET REPODIR=d:\path-to-your-repository
SET REPOBACKUP="C:\path-to-your-backup\svnbackup"

ECHO ==================================
ECHO        PROCESSING BACKUP ...
ECHO  This may take some time depending
ECHO     on the size of your repository!
ECHO ==================================

RMDIR %REPOBACKUP% /S/Q

svnadmin hotcopy %REPODIR% %REPOBACKUP%

ECHO         BACKUP COMPLETED!

