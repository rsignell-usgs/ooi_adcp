#!/usr/bin/env python
#
import os,sys
import urllib,urllib2,re
import optparse
from bs4 import BeautifulSoup
import requests

#odir='/home/hunter/Projects/ooi/work/rawdata/'
odir='/home/om/cron/pioneer/adcp/tel/'

url='https://rawdata.oceanobservatories.org/files/'

wfp_moorlist=[ "CP04OSSM",  "CP03ISSM", "CP01CNSM"]

##wfp_moorlist=["CP02PMUI"]
#parse_re = re.compile('href="([^"]*)".*(..-...-.... ..:..).*?(\d+[^\s<]*|-)')
#          # look for          a link    +  a timestamp  + a size ('-' for dir)
ext='adcp.log'

    
def list_files(url):
    
    parts=url.split('/')
    page = requests.get(url).text
    soup = BeautifulSoup(page)
    for anchor in soup.find_all('a'):
        href = anchor.get('href')
        if href.endswith('/'):
             list_files(url +'/' +href)
        else:
            if href.endswith(ext) : 
                ofile=odir+parts[4]+"/"+parts[5]+"_"+href
                print ofile
                urllib.urlretrieve (url+'/'+href,ofile)
            
                
    
#    print filelist
            

def main(argv):
      

    for tag in wfp_moorlist:
        surl=url+tag
        print surl
        for n in range(20):
            print '/D%5.5d/' % n
            surl2=surl+'/D%5.5d/' % n
            list_files(surl2)    
#        print linklist,
#        for idir in linklist:
#            print idir
##            flist=list_files(idir)
#            for ifile in flist:
#                print ifile
#                parts=ifile.split('/')
#                ofile=odir+"/"+tag+"/"+parts[5]+"_"+parts[-1]
#                print ofile
#                
##        
#        

if __name__ == "__main__":

    
    
    
    print 'RUNNING'
    main(sys.argv)