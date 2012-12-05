
/*  
   PSMonitor Sketch by Matthew Painter 16-Jan-2012 
 
   This 'sketch' will monitor the serial port and respond to appropriate commands sent to it.  
   Sketch assumes it is communicating with the associated Powershell PSMonitor 'script'.  
   Example shows how to react and respond to messages with certain headers. Sketch sends PowerShell  
   command to the connected system and then interprets the executed results.  
    
   Compile using USB type: Serial 
*/ 
 
 
#include <Time.h> 
// library here: http://arduino.cc/playground/Code/Time 
 
int ledPin = 11; 
int ExternalLED = 20; //connect your test LED to pin 20 on Teensy 
int ModeZ; 
int PSCmd; 
char c; 
time_t pctime;  
boolean TimeisSet; 
long SecsStart, SecsEnd, SecsElapsed; 
 
//----------------------------------------------------------------------------  
 
void setup()  
{ 
   digitalWrite(ledPin, HIGH); // set the onboard LED on       
   Serial.begin(9600);    
   pinMode(ExternalLED, OUTPUT);      
   delay(2000); 
} 
 
//----------------------------------------------------------------------------  
 
void loop()  
{ 
  ModeZ = GetMode(); //retrieve Mode 0-15 
   
  if (ModeZ == 0) 
  { 
    Serial.println(F("*** Teensy functions programmed on this board ***")); 
    Serial.println(F("0 - This Menu")); 
    Serial.println(F("1 - PC Speaker Beep")); 
    Serial.println(F("2 - Get Teensy Time")); 
    Serial.println(F("3 - Set Teensy Time")); 
    Serial.println(F("4 - ")); 
    Serial.println(F("5 - Get Computer Serial Number")); 
    Serial.println(F("6 - Get PSMonitor Run Time")); 
    Serial.println(F("7 - ")); 
    Serial.println(F("8 - ")); 
    Serial.println(F("9 - Activate Output1 (LED) on Teensy")); 
    Serial.println(F("10- Deactivate Output1 (LED) on Teensy")); 
    Serial.println(F("11- ")); 
    Serial.println(F("12- ")); 
    Serial.println(F("13- ")); 
    Serial.println(F("14- "));   
    Serial.println(F("15- TEST"));     
  } 
    
  if (ModeZ == 1) 
  { 
    Serial.println(F("Teensy makes Computer Beep")); 
    Serial.println(F("PSCmd:[console]::Beep()")); 
  } 
   
  if (ModeZ == 2) 
  {  
    Serial.println(F("The time set on the Teensy is:")); 
    Serial.print(hour()); Serial.print(":"); 
    if(minute() < 10){Serial.print('0');}Serial.print(minute()); Serial.print(":"); 
    if(second() < 10){Serial.print('0');}Serial.println(second());     
  } 
      
  if (ModeZ == 3) 
  { 
    Serial.println(F("Teensy Requests Computer Send Timestamp")); 
    SetTime(); 
  } 
   
  if (ModeZ == 4) 
  { 
    Serial.println(F("Teensy Requests Username")); 
    Serial.println(F("PSCmd:[environment]::username"));  
  } 
    
  if (ModeZ == 5) 
  { 
    Serial.println(F("Teensy Requests Computer Serial Number")); 
    Serial.println(F("PSCmd:(gwmi 'Win32_BIOS').SerialNumber")); 
  } 
     
  if (ModeZ == 6) 
  { 
    Serial.println(F("Teensy Requests PSMonitor Runtime in Seconds")); 
    Serial.println(F("PSCmd:[math]::round((New-TimeSpan ((gps -id $pid).starttime) (Get-Date)).TotalSeconds,0)"));     
  } 
    
  if (ModeZ == 7) 
  { 
  } 
     
  if (ModeZ == 8) 
  { 
  } 
   
  if (ModeZ == 9) 
  { 
    Serial.println(F("LED ON")); 
    digitalWrite(ExternalLED, HIGH); 
  } 
   
  if (ModeZ == 10) 
  { 
    Serial.println(F("LED OFF")); 
    digitalWrite(ExternalLED, LOW);  
  } 
     
  if (ModeZ == 11) 
  { 
  } 
     
  if (ModeZ == 12) 
  { 
  } 
     
  if (ModeZ == 13) 
  { 
  } 
     
  if (ModeZ == 14) 
  { 
  } 
     
  if (ModeZ == 15) 
  { 
    Serial.println(F("Teensy Running script block 15")); 
  } 
} 
 
//----------------------------------------------------------------------------  
 
int GetMode() 
{ 
  //clear read buffer 
  while (Serial.available()){ Serial.read();} 
   
  //attempt to read serial port for 2 seconds 
  SecsStart = now(); 
  do        
  {    
    if (Serial.available()) 
    {  
      c = Serial.read(); 
      if (c == '@') 
      { 
        PSCmd = 0; 
        for(int i=0; i < 2; i++) 
        {    
          c = Serial.read();         
          if( c >= '0' && c <= '9') 
          {    
            PSCmd = (10 * PSCmd) + (c - '0');  
          } 
        } 
        return PSCmd;       
      } 
      //clear read buffer 
      while (Serial.available()){ Serial.read();} 
    } 
 
    //break loop after 2 secs 
    SecsEnd = now(); 
    SecsElapsed = SecsEnd-SecsStart;  
 
  }while(SecsElapsed<2);  
   
  return 16;   
} 
 
//----------------------------------------------------------------------------  
 
void SetTime() 
{ 
  // set time with timestamp transmitted from local PC 
   
  while (Serial.available()){ Serial.read();} //clear read buffer 
   
  TimeisSet = false;     
 
  //send command to PowerShell requesting timestamp be echoed back 
  Serial.println(F("PSCmd:'T'+[math]::round((New-TimeSpan (get-date('1 Jan 1970')) (get-date)).TotalSeconds,0)")); 
         
  delay(250); 
       
  //read timestamp from serial port       
  if(Serial.available() >= 11 ) 
  {        
    do 
    {  
      c = Serial.read();  
      if( c == 'T' )  
      {        
        pctime = 0; 
        for(int i=0; i < 11 -1; i++) 
        {    
          c = Serial.read();         
          if( c >= '0' && c <= '9') 
          {    
            pctime = (10 * pctime) + (c - '0');     
          } 
        } 
      }   
    } while (Serial.available());        
  } 
 
  setTime(pctime);        
  if (timeStatus() == timeSet) 
  { 
    TimeisSet = true; 
  } 
 
  while (Serial.available()){ Serial.read();}   //clear read buffer 
   
  if(TimeisSet) 
  {        
    Serial.print(hour()); Serial.print(":"); 
    if(minute() < 10){Serial.print('0');}Serial.print(minute()); Serial.print(":"); 
    if(second() < 10){Serial.print('0');}Serial.println(second()); 
  } 
} 
#>