#========================================================================
# Created with: SAPIEN Technologies, Inc., PowerShell Studio 2012 v3.0.3
# Created on:   7/13/2012 9:19 AM
# Created by:   Robert Schwinger
# Organization: Siemens Industry Inc.
# Filename:     
#========================================================================

function Get-MediaFolders(
  [ref]$products, #array of hash-tables
  [ref]$editions, #array of hash-tables
  [ref]$media #hash-table of arrays
 ) 

{

 $productArray = @(
  @{"tag"="2008R2"; "hide"=$false},
  @{"tag"="2008"; "hide"=$false},
  @{"tag"="2005"; "hide"=$false}
  @{"tag"="2000"; "hide"=$true}
  )

  $editionArray = @(
  @{"tag"="STD"; "hide"=$false},
  @{"tag"="DEV"; "hide"=$true},
  @{"tag"="EXP"; "hide"=$false}
  )

  $mediaArrays = @{"Show"="ALL"; 
  "2008R2-STD"=@("folder1", "folder2");
  "2008R2-DEV"=@("folder3");
  "2008-DEV"=@("folder4", "folder5")

  }

 # link arrays to the parameters
$products.value = $productArray # passed back by parameter ref
$editions.value = $editionArray # passed back by parameter ref
$media.value = $mediaArrays # passed back by parameter ref
return
}

$products = @()
$editions = @()
$media = @{}

$return = Get-MediaFolders -products ([ref]$products) -editions ([ref]$editions) -media ([ref]$media)

Write-host '$products count and type:' $products.count $products.gettype().fullname
Write-host '$editions count and type:' $editions.count $editions.gettype().fullname
Write-host '$media count and type:' $media.count $media.gettype().fullname