([System.IO.File]::ReadAllText($_.fullname)) 
 dir $pwd -include *.log -rec | gc | out-file .\pingresults.txt 
 
 snmpping -b -s1.3.6.1.4.1.8433.4.2.6.1 10.0.56.142