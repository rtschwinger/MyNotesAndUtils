#!/usr/bin/python

import os

filename="WIFI_Radio_Info.csv"

def read_radios(filename):
    f = open(filename)
    for line in f:
        line = line.strip()
        words = line.split(",")
        if words[2] == 'PTL':
            print words
        
def main():
	read_radios(filename)



  	
if __name__ == '__main__':
  main()
