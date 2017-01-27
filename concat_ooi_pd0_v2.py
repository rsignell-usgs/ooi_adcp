#!/usr/bin/env python
#
import os,sys,fnmatch
import shutil 
import time,datetime
import urllib,urllib2
import json,optparse
import glob


if 'OOI_DATADIR' in os.environ:
   odir = os.path.join(os.environ['OOI_DATADIR'],'adcp','rec','')
else:
   odir='/home/om/cron/pioneer/adcp/rec/'


#
adcp_moorlist=[ "CP03ISSM", "CP04OSSM",   "CP02PMCI", "CP02PMCO", "CP02PMUI",  "CP02PMUO","CP01CNSM"]

#adcp_moorlist=[ "CP03ISSM"]



def main(argv):
    
        for i,tag in enumerate(adcp_moorlist):
            for n in range(15):
                DEP='R%5.5d' % n
               
                filelist=glob.glob(odir+tag+'/'+DEP+'*.000')
                
                if not filelist:
                    print tag+' - '+DEP+' - NO FILES'
                else:
                    ofile=odir+tag+'/'+DEP+'_'+'CONCATENATE.DAT'
                    print ofile
                    destination = open(ofile, 'wb')

                    for afile in filelist:
                        print afile
                        shutil.copyfileobj(open(afile, 'rb'), destination)
                
                    destination.close()
        
        
        
        
        
        
        
if __name__ == "__main__":

    
    
    print 'RUNNING'
    main(sys.argv)

