### set static IP addressing – save as setstatic.ps1
$NICs = Get-WMIObject Win32_NetworkAdapterConfiguration `
| where{$_.IPEnabled -eq “TRUE”}
Foreach($NIC in $NICs) {
  $NIC.EnableStatic(“190.168.200.5", “255.255.255.0")
  $NIC.SetGateways(“192.168.200.1")
  $DNSServers = “192.168.200.1",”192.168.200.2"
  $NIC.SetDNSServerSearchOrder($DNSServers)
  $NIC.SetDynamicDNSRegistration(“FALSE”)
}
###