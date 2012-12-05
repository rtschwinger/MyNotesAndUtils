$radios = Import-Csv -Delimiter "," -Path e:\opt\SNMP-Radio-Shutdown\LEMRadioList.csv
$nodes = New-Object System.Collections.ArrayList
foreach ($radio in $radios) {
      		$IpAddress = $radio.IPAddress
      		$nodes.Add($IpAddress)
}
$nodes
$nodes | foreach {[System.Diagnostics.Process]::Start("cmd.exe","/c ping.exe $_ > ${_}.log 2>&1") }
$outpath = .\pingtestresults.log
Get-ChildItem -path $pwd -recurse |?{ ! $_.PSIsContainer } |?{($_.name).contains(".log")} | %{ Out-File -filepath $outpath -inputobject (get-content $_.fullname) -Append}
 