proc createfilehdr { filename } {
		set header1 "<!DOCTYPE NETSCAPE-Bookmark-file-1>"
		set header2 "<!- This is an automatically generated file.  It will be read and overwritten. Do Not Edit! ->"
		set header3 "<TITLE>Bookmarks</TITLE>"
		set header4 "<H1>Bookmarks</H1>"
		set startlisttag "<DL><p>"

		set f [open $filename w+]
		
		puts $f $header1
		puts $f $header2
		puts $f $header3
		puts $f $header4
		puts $f $startlisttag
		
		flush $f
		close $f
		
}	

proc getsite { sitelist folderflags ofile } {
				set startlisttag "<DL><p>"
				set stoplisttag "</DL><p>"
				set leftfoldertag "<DT><H3 FOLDED ADD_DATE=\"\">"
				set rightfoldertag "</DT>"
				set Heading3TagStop "</H3>"
				set LeftAnchorTag "<DT><A HREF=\"http://"
				set MiddleAnchorTag "\" ADD_DATE=\"\" LAST_VISIT=\"\" LAST_MODIFIED=\"\">"
				set RightAnchorTag "</A>"
				set f [open $ofile a]
					if { ! [ lindex $folderflags 0 ] } {
						puts $f "\t\t\t\t$leftfoldertag[lindex $sitelist 0 ]$rightfoldertag"
					}
					if { [ lindex $sitelist 2 ] == "9610-PM" } {
							if { ! [ lindex $folderflags 2 ] } {
									puts $f "\t\t\t\t\t\t\t$leftfoldertag[ lindex $sitelist 2 ]$Heading3TagStop"
							}
							puts $f "\t\t\t\t\t\t\t\t\t$LeftAnchorTag[ lindex $sitelist 4 ]$MiddleAnchorTag[ lindex $sitelist 3 ]$RightAnchorTag"
					} elseif { [ lindex $sitelist 2 ] == "9510-RTU" } {
							if { ! [ lindex $folderflags 2 ] } {
									set site "9510-RTU"
									puts $f "\t\t\t\t\t\t\t$leftfoldertag$site$Heading3TagStop"
									set ADRfolderflag 1
							}
							puts $f "\t\t\t\t\t\t\t\t\t$LeftAnchorTag[ lindex $sitelist 4 ]$MiddleAnchorTag[ lindex $sitelist 3 ]$RightAnchorTag"
			 		} elseif { [ lindex $sitelist 2 ] == "CBLOX" } {
			 				if { ! [ lindex $folderflags 2 ]  } {
									puts $f "\t\t\t\t\t\t\t$leftfoldertag[ lindex $sitelist 2 ]$Heading3TagStop"
							}
			 				puts $f "\t\t\t\t\t\t\t\t\t$LeftAnchorTag[ lindex $sitelist 4 ]$MiddleAnchorTag[ lindex $sitelist 3 ]$RightAnchorTag"
					}
					flush $f
					close $f
}

set outfile "./testbookmarks.htm"
createfilehdr $outfile 
set filepath "./DeviceDBDump.csv"
set ioChan [ open $filepath "r" ]

set i 0
set bmdata {}
while { ![eof $ioChan] } {
			set bytes [ gets $ioChan currentline ]
			puts "Current Line $currentline"
		 	set fields [ split $currentline "," ]
		 	set Group [ lindex $fields 1 ]
		 	set SubGroup [ lindex $fields 2 ]
		 	set DeviceGroup [ lindex $fields 3 ]
		 	set DeviceName [ lindex $fields 4 ]
		 	set Address [ lindex $fields 5 ]
		 	# Put desired sort fields together for sorting
			set bmset [list "$Group,$DeviceGroup" $SubGroup $DeviceName $Address]
			incr i
			#puts "Current Line $i:[ lindex $bmset 0 ]:[ lindex $bmset 1 ]:[ lindex $bmset 2 ]:[ lindex $bmset 3 ]"
			append bmdata $bmset
}
close $ioChan


puts "BMDATA $bmdata"

# Sort by site
set sortedbmdata [ lsort -dictionary -index 0 $bmdata ]
#puts "SORTEDDATA $sortedbmdata" 
	
for {set i 0} {$i < [llength $sortedbmdata]} {incr i} {		
	#puts "Entire List Sorted [ lindex $sortedbmdata $i ]"
	#Sorting finished take desired sort fields apart
	set fields [split [lindex $sortedbmdata $i 0] ","] 
	set Group [lindex $fields 0]
	#puts "Group $Group" 
	set DeviceGroup [lindex $fields 1]
	#puts "DeviceGroup $DeviceGroup"
	set SubGroup [lindex $sortedbmdata $i 1]
 	set DeviceName [lindex $sortedbmdata $i 2]
	set Address [lindex $sortedbmdata $i 3]
	set bmset [list $Group $SubGroup $DeviceGroup $DeviceName $Address]
	append finalbmdata $bmset
}
#puts "FINAL SORT $finalbmdata"

global flagslist
for {set i 0} {$i < 18 } {incr i} {
	set flaglist [ list 0 0 0 0 ]
	#puts "FL site $i - 0:[ lindex $flaglist 0 ] 1:[ lindex $flaglist 1 ] 2:[ lindex $flaglist 2 ] 3:[ lindex $flaglist 3 ]"
}


for {set i 0} {$i < [llength $finalbmdata]} {incr i} {
	if { [ lindex $record 0 ] == "USS1" } {
		getsite $record $flaglist $outfile
	}	elseif { [ lindex $record 0 ] == "USS2" } {
		getsite $record $flaglist $outfile 
	} elseif { [ lindex $record 0 ] == "USS3" } {
		getsite $record $flaglist $outfile           
	} elseif { [ lindex $record 0 ] == "USS4" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS5" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS6" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS7" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS8" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS9" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS10" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USS11" } {
		getsite $record $flaglist $outfile           
	} elseif { [ lindex $record 0 ] == "USSMBP" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USSR" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "USSRM" } {
		getsite $record $flaglist $outfile           
	}	elseif { [ lindex $record 0 ] == "UTS" } {
		getsite $record $flaglist $outfile           
	} elseif { [ lindex $record 0 ] == "CDP" } {
		getsite $record $flaglist $outfile           
	} elseif { [ lindex $record 0 ] == "GPS" } {
		getsite $record $flaglist $outfile
	}
}

