<#
.SYNOPSIS
This checks remote computers or devices for open TCP ports by attempting a TCP socket
connection to the specified port or ports using the .NET Net.Sockets.TcpClient class.

.DESCRIPTION
Use the parameter -ComputerName to specify the target computer(s), and the parameter
-Port to specify port(s) to check.

Examples:
.\Get-OpenPort.ps1 -Comp server01 -Port 3389, 445, 80 -Ping
.\Get-OpenPort.ps1 -Comp (gc hosts.txt) -Port 22,80 -Ping -AsJob

Copyright (c) 2012, Svendsen Tech.
All rights reserved.
Author: Joakim Svendsen

More extensive documenatation online:
http://www.powershelladmin.com
http://www.powershelladmin.com/wiki/Check_for_open_TCP_ports_using_PowerShell

.PARAMETER ComputerName
Target computer name(s) or IP address(es).
.PARAMETER Port
TCP port(s) to check whether are open.
.PARAMETER OutputFile
A CSV file will be created regardless of whether you specify this parameter. The default
file name is "SvendsenTechPorts.csv". Choose your own name with this parameter. The file
will be overwritten without you being prompted if it exists.
.PARAMETER Timeout
Timeout in millliseconds before the script considers a port closed. Default 3000 ms
(3 seconds). For speeding things up. Only in effect when used with the -AsJob parameter.
.PARAMETER AsJob
Use one job for each port connection. This allows you to override the possibly lengthy
timeout from the connecting socket, and a port is considered closed if we haven't been
able to connect within the allowed time. Default 3000 ms. See the -Timeout parameter.
This may be quite resource-consuming!
.PARAMETER Ping
Try to ping the target computer as well if this is specified. By default, the script
skips the port checks on targets that do not respond to ICMP ping and populate the
fields with hyphens for these hosts. Be aware that computers that do not resolve via
DNS/WINS/NetBIOS will also be reported as having failed the ping check.
.PARAMETER ContinueOnPingFail
Try to check the target computer for open ports even if it does not respond to ping. Only
in effect when used together with -Ping. Be aware that computers that do not resolve via
DNS will also be processed like this (and it should report them as "closed").
.PARAMETER NoSummary
Do not display a summary at the end. The summary includes start and end time of the script,
the output file name and Import-Csv run against the output file, piped to
"Format-Table -AutoSize".
#>

param([Parameter(Mandatory=$true)][string[]] $ComputerName,
      [Parameter(Mandatory=$true)][int[]] $Port,
      [string] $OutputFile = 'SvendsenTechPorts.csv',
      [int]    $Timeout = 3000,
      [switch] $AsJob,
      [switch] $Ping,
      [switch] $ContinueOnPingFail,
      [switch] $NoSummary
     )

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$StartTime = Get-Date

if ($Timeout -ne 3000 -and -not $AsJob)  { Write-Host -Fore Red "Warning. Timeout not in effect without -AsJob" }
if ($ContinueOnPingFail -and -not $Ping) { Write-Host -Fore Red "Warning. -ContinueOnPingFail not in effect without -Ping" }

# Main data hash. Assumes computer names are unique. If the same computer is
# specified multiple times, it will be processed multiple times, and the data
# from the last time it was processed will overwrite the older data.
$Data = @{}

# Process each computer specified.
foreach ($Computer in $ComputerName) {
    
    # Initialize a new custom PowerShell object to hold the data.
    $Data.$Computer = New-Object PSObject
    
    # Try to ping if -Ping was specified.
    if ($Ping) {
        
        if (Test-Connection -Count 1 -ErrorAction SilentlyContinue $Computer) {
            
            # Produce output to the pipeline and add data to the object.
            "${Computer}: Responded to ICMP ping."
            Add-Member -Name 'Ping' -Value 'Yes' -MemberType NoteProperty -InputObject $Data.$Computer
            
        }
        
        else {
            
            # Produce output to the pipeline and add data to the object.
            "${Computer}: Did not respond to ICMP ping."
            Add-Member -Name 'Ping' -Value 'No' -MemberType NoteProperty -InputObject $Data.$Computer
            
            # If -ContinueOnPingFail was not specified, do this:
            if (-not $ContinueOnPingFail) {
                
                # Set all port states to "-" (not checked).
                foreach ($SinglePort in $Port) {
                    Add-Member -Name $SinglePort -Value '-' -MemberType NoteProperty -InputObject $Data.$Computer
                }
                
                # Continue to the next iteration/computer in the loop.
                continue
                
            }
            
        }
        
    }
    
    # Here we check if the ports are open and store data in the object.
    foreach ($SinglePort in $Port) {
        
        if ($AsJob) {
            
            # This implementation using jobs is to support a custom timeout before proceeding.
            # Default: 3000 milliseconds (3 seconds).
            
            $Job = Start-Job -ArgumentList $Computer, $SinglePort -ScriptBlock {
                
                param([string] $Computer, [int] $SinglePort)
                
                # Create a new Net.Sockets.TcpClient object to use for testing open TCP ports.
                # It needs to be created inside the job's script block.
                $Socket = New-Object Net.Sockets.TcpClient
                
                # Suppress error messages
                $ErrorActionPreference = 'SilentlyContinue'
                
                # Try to connect
                $Socket.Connect($Computer, $SinglePort)
                
                # Make error messages visible again
                $ErrorActionPreference = 'Continue'
                
                if ($Socket.Connected) {
                    
                    # Close the socket.
                    $Socket.Close()
                    
                    # Return success string
                    'connected'
                    
                }
                 
                else {
                    
                    'not connected'
                    
                }
            
            } # end of script block
            
            # If we check the state of the job without a little nap, we'll probably have to
            # sleep longer because it hasn't finished yet. About 250 ms seems to work in my environment.
            # Adding a little... Maybe I should make this a parameter to the script as well.
            Start-Sleep -Milliseconds 400
            
            if ($Job.State -ne 'Completed') {
                
                #'Sleeping...'
                Start-Sleep -Milliseconds $Timeout
                
            }
            
            if ($Job.State -eq 'Completed') {
                
                # Get the results (either 'connected' or 'not connected' - probably 'connected' here...)
                $JobResult = Receive-Job $Job
                
                if ($JobResult -ieq 'connected') {
                    
                    # Produce output to the pipeline and add data to the object.
                    "${Computer}: Port $SinglePort is open"
                    Add-Member -Name $SinglePort -Value 'Open' -MemberType NoteProperty -InputObject $Data.$Computer
                    
                    
                }
                
                else {
                    
                    # Produce output to the pipeline and add data to the object.
                    "${Computer}: Port $SinglePort is closed or filtered"
                    Add-Member -Name $SinglePort -Value 'Closed' -MemberType NoteProperty -InputObject $Data.$Computer
                    
                }
                
            }
            
            # Assume we couldn't connect within the timeout period.
            else {
                
                # Produce output to the pipeline and add data to the object.
                "${Computer}: Port $SinglePort is closed or filtered (timeout: $Timeout ms)"
                Add-Member -Name $SinglePort -Value 'Closed (t)' -MemberType NoteProperty -InputObject $Data.$Computer
                
            }
            
            # Stopping and removing the job causes it to wait beyond the timeout... Let's accumulate crap.
            #Stop-Job -Job $Job
            #Remove-Job -Force -Job $Job
            
            $Job = $null
            
        } # end of if ($AsJob)
        
        # Do it the usual way without jobs. No custom timeout support.
        else {
            
            # Create a new Net.Sockets.TcpClient object to use for testing open TCP ports.
            $Socket = New-Object Net.Sockets.TcpClient
            
            # Suppress error messages
            $ErrorActionPreference = 'SilentlyContinue'
            
            # Try to connect
            $Socket.Connect($Computer, $SinglePort)
            
            # Make error messages visible again
            $ErrorActionPreference = 'Continue'
            
            if ($Socket.Connected) {
                
                # Produce output to the pipeline and add data to the object.
                "${Computer}: Port $SinglePort is open"
                Add-Member -Name $SinglePort -Value 'Open' -MemberType NoteProperty -InputObject $Data.$Computer
                
                # Close the socket.
                $Socket.Close()
                
            }
             
            else {
                
                # Produce output to the pipeline and add data to the object.
                "${Computer}: Port $SinglePort is closed or filtered"
                Add-Member -Name $SinglePort -Value 'Closed' -MemberType NoteProperty -InputObject $Data.$Computer
                
            }
            
            # Reset the variable. Apparently necessary.
            $Socket = $null
            
        }
        
    } # end of foreach port
    
} # end of foreach computer

# Will surround each element in an array of string with double quotes
# and join them together with commas. Returns the CSV string.
function Format-AsCsv {
    
    param([Parameter(Mandatory=$true)][string[]] $String)
    
    $CsvString = ($String | ForEach-Object { '"' + $_ + '"' }) -join ','
    
    $CsvString
    
}

# Create CSV headers
$Headers = @()
$Headers += 'ComputerName'

# Add the ping header if -Ping was specified.
if ($Ping) { $Headers += 'Ping' }

# Sort ports numerically and add them after computer name and possibly the ping column.
$Headers += $Port | Sort-Object | ForEach-Object { "Port $_" }

# Initialize CSV data array and add the headers.
$Csv = @()
$Csv += Format-AsCsv $Headers

$Data.GetEnumerator() | ForEach-Object {
    
    # Store the value object for later use.
    $InstanceData = $_.Value
    
    # Initialize array with temporary data.
    $InstanceDataArray = @()
    
    # Add the host name
    $InstanceDataArray += $_.Name
    
    # If -Ping was supplied, add a ping field to the CSV data.
    if ($Ping) { $InstanceDataArray += $InstanceData.Ping }
    
    # Doing this to get numerical sort of port numbers.
    $MemberNames = Get-Member -MemberType NoteProperty -InputObject $InstanceData |
        Where-Object { $_.Name -ine 'Ping' } |
        Select-Object -ExpandProperty Name
    
    # Cast to int and sort numerically. Retrieve data from object.
    [int[]] $MemberNames | Sort-Object | ForEach-Object { $InstanceDataArray += $InstanceData.$_ }
    
    # Format string as CSV and add to the CSV data array.
    $Csv += Format-AsCsv $InstanceDataArray
    
}

# Save data to CSV file (default: SvendsenTechPorts.csv).
$Csv | Set-Content -Encoding utf8 $OutputFile

# Display summary results.
if (-not $NoSummary) {
    
@"

Start time:  $StartTime
End time:    $(Get-Date)

Output file: $OutputFile

"@
    
    # Display the CSV data (I figured this would be useful in most cases...).
    # Thought about making it optional with yet another switch parameter.
    Import-Csv $OutputFile | Format-Table -AutoSize
    
}
