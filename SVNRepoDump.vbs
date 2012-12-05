Const ForReading = 1
Const ForWriting = 2
Const ForAppending = 8

Const folderName = "f:\backup\dumps\"
Const repositoryProj1 = "F:\ProjectRepos\GIMP_Addons"
Const repositoryProj2 = "F:\ProjectRepos\MSN_CH1"
Const repositoryProj3 = "F:\ProjectRepos\My_Utils"
Const repositoryProj4 = "F:\ProjectRepos\PowerLoft"
Const repositoryProj5 = "F:\ProjectRepos\SolarWorld"
Const repositoryProj6 = "F:\ProjectRepos\Surabaya"
Const repositoryProj7 = "F:\ProjectRepos\svn_files"

'getYoungestProj1 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj1
'getYoungestProj2 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj2
'getYoungestProj2 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj3
'getYoungestProj2 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj4
'getYoungestProj2 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj5
'getYoungestProj2 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj6
'getYoungestProj2 = "C:\Program Files\VisualSVN Server\bin\svnlook.exe youngest " + repositoryProj7

Set objFSO = CreateObject( "Scripting.FileSystemObject" )
Set WshShell = CreateObject( "WScript.Shell" )

Call CreateDump( "f:\backup\proj1.log", "F:\ProjectRepos\proj1-last", 0, repositoryProj1, "GIMP_Addons" )
Call CreateDump( "f:\backup\proj2.log", "F:\ProjectRepos\proj2-last", 0, repositoryProj2, "MSN_CH1" )
Call CreateDump( "f:\backup\proj3.log", "F:\ProjectRepos\proj3-last", 0, repositoryProj3, "My_Utils" )
Call CreateDump( "f:\backup\proj4.log", "F:\ProjectRepos\proj4-last", 0, repositoryProj4, "PowerLoft" )
Call CreateDump( "f:\backup\proj5.log", "F:\ProjectRepos\proj5-last", 0, repositoryProj5, "SolarWorld" )
Call CreateDump( "f:\backup\proj6.log", "F:\ProjectRepos\proj6-last", 0, repositoryProj6, "Surabaya" )
Call CreateDump( "f:\backup\proj6.log", "F:\ProjectRepos\proj7-last", 0, repositoryProj7, "svn_files" )

WScript.Quit( 0 )

'********************************************************************************
'*
'* End of script body
'*
'********************************************************************************

Sub CreateDump( logFileName, lastFileName, getYoungestCmd, repository, dumpName )

  ' Open the log file
  Set objLogFile = objFSO.OpenTextFile( logFileName, ForAppending, True )
  objLogFile.WriteLine Now & " - - Script started - -"
  
  ' Default last revision is 0
  lastRev = 0
  
  ' Does the file exist?
  If ( objFSO.FileExists( lastFileName ) ) Then
    Set objFile = objFSO.GetFile( lastFileName )
    ' Does it contain anything?
    If ( objFile.Size > 0 ) Then
      Set objTextFile = objFSO.OpenTextFile( lastFileName, ForReading )
      ' Get the last revison and increase it by 1
      lastRev = objTextFile.Readline
      lastRev = lastRev + 1
    End If
  End If
  
  ' Execute the getYoungestCmd and read its output
  Set objExec = WshShell.Exec( getYoungestCmd )
  
  Do While ( objExec.Status <> 1 )
       WScript.Sleep 100
  Loop
  
  youngest = objExec.StdOut.Readline
  
  ' Is the youngest revision above the last one?
  If ( CLng( lastRev ) > CLng( youngest ) ) Then
    objLogFile.WriteLine Now & "   Exiting: lastRev (" & lastRev & ") > youngest (" & youngest & ")"
    objLogFile.WriteLine Now & "     Script done"
    objLogFile.Close
    Exit Sub
  End If
  
  ' Compose the file name
  dumpFileName = folderName & dumpName & "-" & lastRev & "-" & youngest & ".dmp"
  
  ' Add incremental, if not starting a new dump
  incremental = ""
  If ( lastRev > 0 ) Then
    incremental = " --incremental"
  End If
  
  ' Compose the dump command for the current repository
  dumpCommand = "C:\Progra~1\Subversion\bin\svnadmin.exe dump " & repository & _
                " --revision " & lastRev & ":" & youngest & incremental
  
  ' Open the destination file and execute the dump command
  Set objDumpFile = objFSO.OpenTextFile( dumpFileName, ForWriting, True )
  Set objExecDump = WshShell.Exec( dumpCommand )
  
  ' Read the dump output and write it to the file
  Do While True
       If Not objExecDump.StdOut.AtEndOfStream Then
            input = objExecDump.StdOut.Read( 1 )
            objDumpFile.Write input
       Else
         Exit Do
       End If
  Loop
  objDumpFile.Close
  
  ' Write the latest revision into the file
  Set objTextFile = objFSO.OpenTextFile( lastFileName, ForWriting, True )
  objTextFile.Write youngest
  objTextFile.Close
  
  ' Close the log file and exit
  objLogFile.WriteLine Now & "     Script done"
  objLogFile.Close
  
End Sub