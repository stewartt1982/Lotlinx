#!/usr/bin/env python
import json
import copy
import time
import os
import sys
import argparse
#The optimizer funtions are in this module
import optimizer


def main():
    parser = argparse.ArgumentParser(prog='optimize_photos',description='Submit photos to the LotLinx PhotoAI optimizer')
    parser.add_argument("-f", "--file", dest="filename",type=argparse.FileType('r'),
                        help="input file containing a list of URLs to process", metavar="FILE")
    parser.add_argument("-t", "--timeout", dest="timeout",type=int,default=100,
                        help="timeout to control how long the program should wait to download files in seconds", metavar="TIMEOUT")
    parser.add_argument("-u", "--username", dest="username",type=str,default="",
                        help="username for PhotoAI", metavar="USERNAME")
    parser.add_argument("-p", "--password", dest="password",type=str,default="",
                        help="password for PhotoAI", metavar="PASSWORD")
    parser.add_argument("-d", "--dealer", dest="dealer",type=int,default=1,
                        help="dealer number/name", metavar="DEALER")
    parser.add_argument("-o", "--output", dest="output",type=str,default="./",
                        help="output directory", metavar="DIR")
    parser.add_argument('URL', type=str, nargs='*',help="1 or more URLs to images. Required if -f/--file is not used")
    args = parser.parse_args()

    #Process command line arguments
    urls = []
    #Deal with passed urls
    if args.filename is not None:
        for l in args.filename:
            urls.append(l.rstrip())

    #Append any urls given as optional commandline arguments
    if len(args.URL) != 0:
        for url in args.URL:
            urls.append(url.rstrip())

    #Check if there was a redirect from stdin. only accept if there is
    #no inpt from file or optional arguments

    if len(urls) == 0:
        for line in sys.stdin:
            urls.append(line.rstrip())
            
    #Check if there are no passed URLs
    if len(urls) == 0:
        #exit
        print "ERROR: No URLs passed to optimize_photos\n"
        print sys.exit(1)
        
    if args.password is not None:
        password = args.password
    if args.username is not None:
        username = args.username
    if args.dealer is not None:
        dealer = args.dealer
    if args.output is not None:
        path = args.output
    if args.timeout is not None:
        timeout=args.timeout
            
    #Run PhotoAI optimizer
    logging = open("logging.txt","w")
    optimizer.optimizeFiles(dealer=dealer,files=urls,passwrd=password,user=username,path=path,timeout=timeout,logfile=logging)
    logging.close()
    
if __name__=='__main__':
    main()
