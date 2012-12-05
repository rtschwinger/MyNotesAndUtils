### set static IP addressing – save as setstatic.ps1
$NICs = Get-WMIObject Win32_NetworkAdapterConfiguration `
| where{$_.IPEnabled -eq “TRUE”}
Foreach($NIC in $NICs) {
  $NIC.EnableStatic(“10.128.56.157", “255.255.0.0")
  $NIC.SetGateways(“10.128.56.1")
  #$DNSServers = “10.10.10.1",”10.10.10.2"
  #$NIC.SetDNSServerSearchOrder($DNSServers)
  #$NIC.SetDynamicDNSRegistration(“FALSE”)
}
###