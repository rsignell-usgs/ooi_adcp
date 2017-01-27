#!/usr/bin/env python
#
import os,sys
import urllib,urllib2,re
import optparse
from bs4 import BeautifulSoup
import requests

if 'OOI_DATADIR' in os.environ:
   odir = os.path.join(os.environ['OOI_DATADIR'],'adcp','rec','')
else:
   odir='/home/om/cron/pioneer/adcp/rec/'

url='https://rawdata.oceanobservatories.org/files/'
#
wfp_moorlist=[ "CP02PMCI", "CP02PMCO", "CP02PMUI",  "CP02PMUO","CP01CNSM","CP03ISSM","CP04OSSM"]


ext='000'



                
                
def list_files(url):
    
    parts=url.split('/')
    page = requests.get(url).text
    soup = BeautifulSoup(page,'html_parser')
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
        mooring_dir = os.path.join(odir,tag)
        if not os.path.exists(mooring_dir):
            os.makedirs(mooring_dir)
        for n in range(20):
            print '/R%5.5d/' % n
            surl2=surl+'/R%5.5d/' % n
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
