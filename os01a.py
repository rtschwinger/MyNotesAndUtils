#!/usr/bin/python
# os01a.py
# Bernard Sypniewski
# This file demonstrates some ways that we can use the os module
# to manipulate the operating system. Since PYTHON is cross-
# platform, some of the results here will differ on different
# operating systems like the MAC OS or LINUX.
#
import os

print "This script demonstrates ways to find out things about the operating system"
print "that you are working with and ways to use the system to display files. The first"
print "several lines display information which you might need when parsing or assembling"
print "strings for file handling. You should be using PYTHON version 2.5. Some commands"
print "may not work properly or at all with earlier versiion."
print
print "The string or character that represents the parent directory is ", os.pardir
print "The current path is: ", os.curdir
print "The character used to separate directories in a path is ", os.sep
print "If there is an alternate separator it is ", os.altsep
print "The character which separates the filename from the extension is ", os.extsep
print "The character which separates the components in searches is ", os.pathsep
print "The default search path is ", os.defpath
print
dummy = raw_input("Press ENTER to see README.TXT in the program that is associated with .TXT files")
os.startfile("readme.txt")
print
dummy = raw_input("Press ENTER to see the class text in ADOBE ACROBAT READER (or ACROBAT itself if it installed)")
os.system('start thinkCSpy.pdf')
print
dummy = raw_input("Press ENTER to see the code for this file in NOTEPAD - this will not work on systems other than WINDOWS")
os.system('start notepad.exe os01a.py')
print
print "The following lines assemble the command to start the program from instantiated variables."
print "Notice that the command is run when the PRINT command executes."
dummy = raw_input("Press ENTER to see the code for this file")
fn = "os01a.py"
pn = "notepad.exe"
cn = "'start(\""
ce = "\"')"
startString=cn + pn + fn + ce
print startString