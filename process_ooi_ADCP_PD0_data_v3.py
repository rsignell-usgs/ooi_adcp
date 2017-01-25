#!/usr/bin/env python
#
import os,sys
sys.path.append('/home/om/cron/pioneer/adcp/rec')
import glob,optparse
from trdi_adcp_readers.pd0.pd0_parser import parse_pd0_bytearray
from trdi_adcp_readers.pd0.pd0_parser import parse_fixed_header
import numpy as np
import matplotlib,netCDF4
import matplotlib.pyplot as plt
import datetime
import struct
#
rtime=datetime.datetime(2013,01,01,00,00,00)

odir='/home/om/cron/pioneer/adcp/rec/'

#moorlist=[ "CP03ISSM", "CP04OSSM",   "CP02PMCI", "CP02PMCO", "CP02PMUI",  "CP02PMUO","CP01CNSM"]
#mlat=[39.94,40.36,40.2266,40.0961,40.3634,39.9416,40.1332] 
#mlon=[-70.88,-70.88,-70.8886,-70.8797,-70.7760,-70.7784,-70.8884]


mlat={"CP03ISSM":40.359,"CP04OSSM":39.94,"CP02PMCI":40.2266,"CP02PMCO":40.0961, "CP02PMUI":40.3634,"CP02PMUO":39.9416,"CP01CNSM":40.140} 
mlon={"CP03ISSM":-70.885,"CP04OSSM":-70.877,"CP02PMCI":-70.8886,"CP02PMCO":-70.8797, "CP02PMUI":-70.7760,"CP02PMUO":-70.7784,"CP01CNSM":-70.772}
bcut={"CP03ISSM":70,"CP04OSSM":300,"CP02PMCI":100,"CP02PMCO":100, "CP02PMUI":65,"CP02PMUO":300,"CP01CNSM":100}
def main(argv):
    
    print opts.mooring    
    moorlist=opts.mooring.split(':')
    for [im, moor] in enumerate(moorlist):
        lat=mlat[moor]
        lon=mlon[moor]
        for n in range(20):
            
            DEP='R%5.5d' % n
            infile=glob.glob(odir+moor+'/'+DEP+'_'+'CONCATENATE.DAT') 
            ofile=odir+'PIONEER_ADCP_RECOVERED_'+moor+'_'+DEP+'.nc'
            if not infile:
               print moor+' - '+DEP+' - NO FILES'
            else:
                read_write_PD0(moor,infile[0],ofile,lat,lon)
    
def read_write_PD0(moor,fil,ncofile,lat,lon):
    print 'PROCESSING_ADCP'
    print fil
    print ncofile    


    f=open(fil,'rb')
    dat = bytearray(f.read())
        
    for [ind,tmp1] in enumerate(dat):
         if hex(dat[ind])=='0x7f' and hex(dat[ind+1]) =='0x7f':
                 break
    a=buffer(dat,ind+2,2)
    nbytes=struct.unpack("h",a)[0]+2


##    
    print 'Finding Ensembles'       
    Iens=[]
    nind=0
    for [ind,tmp1] in enumerate(dat):
         if hex(dat[ind])=='0x7f' and hex(dat[ind+1]) =='0x7f':
             
                    
             startens=(ind)
             tdat=dat[startens:startens+nbytes]
             if len(tdat)<nbytes:
                 break
             a=buffer(tdat,nbytes-2,2)
             chksum=struct.unpack("<H",a)[0]
             if (sum(tdat[:nbytes-2]) & 65535) ==  chksum:
                 nind=ind
                 Iens.append(ind)
#                 
#                 print '-+++++'   
#                 print len(Iens)
                 
#             
    nens=len(Iens) 

    print 'creating arrays'
    time=np.empty((nens),np.float)    
    pressure=np.empty((nens),np.float) 
    pitch=np.empty((nens),np.float) 
    roll=np.empty((nens),np.float) 
    heading=np.empty((nens),np.float) 
    temp=np.empty((nens),np.float) 
#        
    u=np.empty((nens,100),np.float) 
    v=np.empty((nens,100),np.float) 
    w=np.empty((nens,100),np.float)
    err=np.empty((nens,100),np.float)  
    ei1=np.empty((nens,100),np.float) 
    ei2=np.empty((nens,100),np.float) 
    ei3=np.empty((nens,100),np.float)
    ei4=np.empty((nens,100),np.float)  
    c1=np.empty((nens,100),np.float) 
    c2=np.empty((nens,100),np.float) 
    c3=np.empty((nens,100),np.float)
    c4=np.empty((nens,100),np.float)             
    print 'loop'
    ind=0
    eoffset=0
    for ind2 in Iens:
#        print '---'
      #  print eoffset
        startens=(ind2)
        tdat=dat[startens:startens+nbytes]
        a=buffer(tdat,2,2)
        tnbytes=struct.unpack("H",a)[0]+2
        a=buffer(tdat,nbytes-2,2)
        chksum=struct.unpack("<H",a)[0]
        if (sum(tdat[:nbytes-2]) & 65535) ==  chksum:

            a=buffer(tdat,5,1)
            ndtype=struct.unpack("b",a)[0]
            offsets=list()
            for ind3 in range(ndtype):
                a=buffer(tdat,6+ind3*2,2)
                offsets.append(struct.unpack_from("h",a)[0])
                
                             
            #FIXEDLEADER
            a=buffer(tdat,offsets[0]+8,1)
  #          nbeam=struct.unpack("b",a)[0]  
            
            a=buffer(tdat,offsets[0]+9,1)
            ncells=struct.unpack("b",a)[0]    
            a=buffer(tdat,offsets[0]+12,2)
            cellsize=struct.unpack("H",a)[0]        
            cellsize=cellsize/100.0       
            a=buffer(tdat,offsets[0]+32,2)
            bin1=struct.unpack("H",a)[0]    
            bin1=bin1/100.0
            
            #variableleader
#            
            a=buffer(tdat,offsets[1]+2,2)
            ens=struct.unpack("H",a)[0]        
            a=buffer(tdat,offsets[1]+4,1)
            year=struct.unpack("b",a)[0]  
            a=buffer(tdat,offsets[1]+5,1)
            month=struct.unpack("b",a)[0] 
            a=buffer(tdat,offsets[1]+6,1)
            day=struct.unpack("b",a)[0] 
            a=buffer(tdat,offsets[1]+7,1)
            hour=struct.unpack("b",a)[0] 
            a=buffer(tdat,offsets[1]+8,1)
            minute=struct.unpack("b",a)[0] 
            a=buffer(tdat,offsets[1]+9,1)
            sec=struct.unpack("b",a)[0] 
            a=buffer(tdat,offsets[1]+10,1)
            hsec=struct.unpack("b",a)[0] 
         #   print [year+2000,month,day,hour,minute,sec,hsec*10]
            ttime = datetime.datetime(year+2000,month,day,hour,minute,sec,hsec*10)-rtime
#            trtime = datetime.datetime(year+2000,month,day,hour,minute,sec,hsec)
#            print trtime
            a=buffer(tdat,offsets[1]+18,2)
            theading=struct.unpack("H",a)[0]        
            theading=theading/100.0    
            a=buffer(tdat,offsets[1]+20,2)
            tpitch=struct.unpack("h",a)[0]        
            tpitch=tpitch/100.0    
            a=buffer(tdat,offsets[1]+22,2)
            troll=struct.unpack("h",a)[0]        
            troll=troll/100.0    
            
            a=buffer(tdat,offsets[1]+26,2)
            ttemp=struct.unpack("h",a)[0]        
            ttemp=ttemp/100.0       
            
            a=buffer(tdat,offsets[1]+48,4)
            tpress=struct.unpack("i",a)[0]        
            tpress=tpress/1000.0       
            
            
    #        print theading,tpitch,troll,ttemp,tpress
            #velocity data 
            a=buffer(tdat,offsets[2]+2,ncells*4*2)
#            print ncells*4*2
            fmt = "<%dh" % (ncells*4)
            uvw=struct.unpack(fmt,a)
            uvw=np.array(uvw)
            
            #EI data 
            a=buffer(tdat,offsets[3]+2,ncells*4)
            fmt = "<%dB" % (ncells*4)
            tEI=struct.unpack(fmt,a)
            tEI=np.array(tEI)
            
            #C data 
            a=buffer(tdat,offsets[4]+2,ncells*4)
            fmt = "<%dB" % (ncells*4)
            tC=struct.unpack(fmt,a)
            tC=np.array(tC)
            
            uvw.shape=(ncells,4)
            tEI.shape=(ncells,4)
            tC.shape=(ncells,4)
#            time=np.append(time,ttime.days+ttime.seconds/86400.0)
#            pressure=np.append(pressure,tpress)
#            pitch=np.append(pitch,tpitch)
#            roll=np.append(roll,troll)
#            temp=np.append(temp,ttemp)
#            heading=np.append(heading,theading)
            
#            u=np.concatenate((u,uvw[:,0]))
#            v=np.concatenate((v,uvw[:,1]))
#            w=np.concatenate((w,uvw[:,2]))
#            err=np.concatenate((err,uvw[:,3]))
#        
#            ei1=np.concatenate((ei1,tEI[:,0]))
#            ei2=np.concatenate((ei2,tEI[:,1]))
#            ei3=np.concatenate((ei3,tEI[:,2]))
#            ei4=np.concatenate((ei4,tEI[:,3]))
#        
#            c1=np.concatenate((c1,tC[:,0]))
#            c2=np.concatenate((c2,tC[:,1]))
#            c3=np.concatenate((c3,tC[:,2]))
#            c4=np.concatenate((c4,tC[:,3]))
#            print ttime.days
            time[ind]=ttime.days+ttime.seconds/86400.0
      
            pressure[ind]=tpress
            pitch[ind]=tpitch
            roll[ind]=troll
            temp[ind]=ttemp
            heading[ind]=theading
            u[ind,0:ncells]=uvw[:,0]
            v[ind,0:ncells]=uvw[:,1]
            w[ind,0:ncells]=uvw[:,2]
            err[ind,0:ncells]=uvw[:,3]
        
            ei1[ind,0:ncells]=tEI[:,0]
            ei2[ind,0:ncells]=tEI[:,1]
            ei3[ind,0:ncells]=tEI[:,2]
            ei4[ind,0:ncells]=tEI[:,3]
        
            c1[ind,0:ncells]=tC[:,0]
            c2[ind,0:ncells]=tC[:,1]
            c3[ind,0:ncells]=tC[:,2]
            c4[ind,0:ncells]=tC[:,3]
            ind=ind+1
        else:
         #   print 'BAD CHECKSUM'
           # eoffset=eoffset+1
            
            continue
     
    
#            
#    nt=len(time)
#    print nt
#        
#    u.shape=(nt,ncells)
#    v.shape=(nt,ncells)
#    w.shape=(nt,ncells)
#    err.shape=(nt,ncells)    
#    
#    
#    ei1.shape=(nt,ncells)
#    ei2.shape=(nt,ncells)
#    ei3.shape=(nt,ncells)
#    ei4.shape=(nt,ncells)    
#    
#    c1.shape=(nt,ncells)
#    c2.shape=(nt,ncells)
#    c3.shape=(nt,ncells)
#    c4.shape=(nt,ncells)  
    u=u[:,0:ncells]
    v=v[:,0:ncells]
    w=w[:,0:ncells]
    err=err[:,0:ncells]

    ei1=ei1[:,0:ncells]
    ei2=ei2[:,0:ncells]    
    ei3=ei3[:,0:ncells]    
    ei4=ei4[:,0:ncells]

    c1=c1[:,0:ncells]
    c2=c2[:,0:ncells]    
    c3=c3[:,0:ncells]    
    c4=c4[:,0:ncells]
    
    ang=np.exp(1j*14.0*np.pi/180.0)
##
    wc=u+1j*v
    wc=wc*ang
    u=wc.real
    v=wc.imag        
#         
#    binsize=4
#    bin1=3
    bins=(np.array(range(ncells))*cellsize)+bin1
    xv, yv = np.meshgrid(pressure, bins)
    xv=xv.transpose()
    yv=yv.transpose() 
    u[yv>xv*0.85]=np.nan
    v[yv>xv*0.85]=np.nan
    w[yv>xv*0.85]=np.nan
    err[yv>xv*0.85]=np.nan
    
    c1[yv>xv*0.85]=np.nan
    c2[yv>xv*0.85]=np.nan
    c3[yv>xv*0.85]=np.nan
    c4[yv>xv*0.85]=np.nan
##  
    ei1[yv>xv*0.85]=np.nan
    ei2[yv>xv*0.85]=np.nan
    ei3[yv>xv*0.85]=np.nan
    ei4[yv>xv*0.85]=np.nan
    
    
#            
##             
#  Depth CUTOFF
    Ibad=np.where(pressure<bcut[moor])
    mask=np.ones(len(time),dtype=bool)
    mask[Ibad]=False
    time=time[mask]        
    pressure=pressure[mask]
    heading=heading[mask]
    pitch=pitch[mask]
    roll=roll[mask]
    temp=temp[mask]
    u=u[mask,:]
    v=v[mask,:]
    w=w[mask,:]
    err=err[mask,:]
    
    ei1=ei1[mask,:]
    ei2=ei2[mask,:]
    ei3=ei3[mask,:]
    ei4=ei4[mask,:]
    
    c1=c1[mask,:]
    c2=c2[mask,:]
    c3=c3[mask,:]
    c4=c4[mask,:]
    if len(time) <10:
        print 'NO GOOD DATA:'+fil
        return
    #SORT
   
    Is = np.argsort(time)
    time=time[Is]        
    pressure=pressure[Is]
    heading=heading[Is]
    pitch=pitch[Is]
    roll=roll[Is]
    temp=temp[Is]
    u=u[Is,:]
    v=v[Is,:]
    w=w[Is,:]
    err=err[Is,:]
    
    
    ei1=ei1[Is,:]
    ei2=ei2[Is,:]
    ei3=ei3[Is,:]
    ei4=ei4[Is,:]
    
    c1=c1[Is,:]
    c2=c2[Is,:]
    c3=c3[Is,:]
    c4=c4[Is,:]
    
    
    time, Is = np.unique(time, return_index=True)
    pressure=pressure[Is]
    heading=heading[Is]
    pitch=pitch[Is]
    roll=roll[Is]
    temp=temp[Is]
    u=u[Is,:]
    v=v[Is,:]
    w=w[Is,:]
    err=err[Is,:]
    
    
    ei1=ei1[Is,:]
    ei2=ei2[Is,:]
    ei3=ei3[Is,:]
    ei4=ei4[Is,:]
    
    c1=c1[Is,:]
    c2=c2[Is,:]
    c3=c3[Is,:]
    c4=c4[Is,:]
    
##    print 'plotting'
#    print 'plot press'
#    plt.figure(1)
#    plt.plot(time,pressure, 'r.-')
####  
#    plt.figure(2)
#    plt.plot(time,heading, 'ro')
###        
##
    
#    print 'plot uvw'
#    plt.figure(3)
##    plt.subplot(4,1,1)
#    plt.pcolor(time,bins,u.transpose(),vmin=-500, vmax=500)
##    plt.subplot(4,1,2)
#    plt.pcolor(time,bins,v.transpose(),vmin=-500, vmax=500)
#    plt.subplot(4,1,3)
#    plt.pcolor(time,bins,w.transpose(),vmin=-500, vmax=500)
#    plt.subplot(4,1,4)
#    plt.pcolor(time,bins,err.transpose(),vmin=-500, vmax=500)
##    
##    plt.figure(4)
##    plt.subplot(4,1,1)
##    plt.pcolor(time,bins,ei1.transpose(),vmin=0, vmax=150)
##    plt.subplot(4,1,2)
##    plt.pcolor(time,bins,ei2.transpose(),vmin=0, vmax=150)
##    plt.subplot(4,1,3)
##    plt.pcolor(time,bins,ei3.transpose(),vmin=0, vmax=150)
##    plt.subplot(4,1,4)
##    plt.pcolor(time,bins,ei4.transpose(),vmin=0, vmax=150)
##    
##    
##    plt.figure(5)
##    plt.subplot(4,1,1)
##    plt.pcolor(time,bins,c1.transpose(),vmin=0, vmax=120)
##    plt.subplot(4,1,2)
##    plt.pcolor(time,bins,c2.transpose(),vmin=0, vmax=120)
##    plt.subplot(4,1,3)
##    plt.pcolor(time,bins,c3.transpose(),vmin=0, vmax=120)
##    plt.subplot(4,1,4)
##    plt.pcolor(time,bins,c4.transpose(),vmin=0, vmax=120)
#    
#    
#    plt.show()
##        
    
#
    print 'outputting'
    ncfile = netCDF4.Dataset(ncofile, 'w', format='NETCDF4')
    ncfile.Conventions= "CF-1.6"
#    
#    
    ncfile.createDimension('time', None)
    ncfile.createDimension('depth', ncells)
    ncfile.createDimension('lat', 1)
    ncfile.createDimension('lon', 1)
    ncfile.createVariable('time','f8',('time',))
    ncfile.createVariable('heading','f8',('time',))
    ncfile.createVariable('pressure','f8',('time',))
    ncfile.createVariable('pitch','f8',('time',))
    ncfile.createVariable('roll','f8',('time',))
    ncfile.createVariable('temperature','f8',('time',))
    ncfile.createVariable('range','f8',('depth',))
    ncfile.createVariable('latitude','f8',('lat',))
    ncfile.createVariable('longitude','f8',('lon',))
    
    ncfile.createVariable('u','f8',('time','depth'))
    ncfile.createVariable('v','f8',('time','depth'))
    ncfile.createVariable('w','f8',('time','depth'))
    ncfile.createVariable('err','f8',('time','depth'))
    
    
    ncfile.createVariable('ei1','f8',('time','depth'))
    ncfile.createVariable('ei2','f8',('time','depth'))
    ncfile.createVariable('ei3','f8',('time','depth'))
    ncfile.createVariable('ei4','f8',('time','depth'))
#        

    ncfile.variables['time'][:]=time
    ncfile.variables['time'].units='days since 2013-01-01 00:00:00'
    ncfile.variables['time'].long_name='time'
    ncfile.variables['time'].standard_name='time'

    
    ncfile.variables['latitude'][:]=lat
    ncfile.variables['latitude'].units='degrees_north'
    ncfile.variables['latitude'].long_name='Latitude'
    ncfile.variables['latitude'].standard_name='latitude'
    
    
    
    ncfile.variables['longitude'][:]=lon
    ncfile.variables['longitude'].units='degrees_east'
    ncfile.variables['longitude'].long_name='Longitude'
    ncfile.variables['longitude'].standard_name='longitude'
#    
    ncfile.variables['range'][:]=bins
    ncfile.variables['range'].units='m'
    ncfile.variables['range'].long_name='range from ADCP'
    ncfile.variables['range'].standard_name='depth'
#    
    ncfile.variables['pressure'][:]=pressure
    ncfile.variables['pressure'].units='dbar'
    ncfile.variables['pressure'].long_name='Pressure'
    ncfile.variables['pressure'].standard_name='sea_water_pressure'

#        
    ncfile.variables['heading'][:]=heading
    ncfile.variables['heading'].units='degrees'
    ncfile.variables['heading'].long_name='heading'
#    

    ncfile.variables['temperature'][:]=temp
    ncfile.variables['temperature'].units='degrees C'
    ncfile.variables['temperature'].long_name='temperature'
#    
    ncfile.variables['pitch'][:]=pitch
    ncfile.variables['pitch'].units='degrees'
    ncfile.variables['pitch'].long_name='pitch'

    ncfile.variables['roll'][:]=roll
    ncfile.variables['roll'].units='degrees'
    ncfile.variables['roll'].long_name='roll'

    ncfile.variables['u'][:]=u/1000.0
    ncfile.variables['u'].units='m s-1'
    ncfile.variables['u'].long_name='eastward water velocity'
    ncfile.variables['u'].standard_name='eastward_sea_water_velocity'

    ncfile.variables['v'][:]=v/1000.0
    ncfile.variables['v'].units='m s-1'
    ncfile.variables['v'].long_name='northward water velocity'
    ncfile.variables['v'].standard_name='northward_sea_water_velocity'

    ncfile.variables['w'][:]=w/1000.0
    ncfile.variables['w'].units='m s-1'
    ncfile.variables['w'].long_name='vertical water velocity'
    ncfile.variables['w'].standard_name='upward_sea_water_velocity'

    ncfile.variables['err'][:]=err/1000.0
    ncfile.variables['err'].units='m s-1'
    ncfile.variables['err'].long_name='error water velocity'
    
    print u.shape
    print ei1.shape
    ncfile.variables['ei1'][:]=ei1
    ncfile.variables['ei1'].units='counts'
    ncfile.variables['ei1'].long_name='beam 1 echo intensity'
    
    ncfile.variables['ei2'][:]=ei2
    ncfile.variables['ei2'].units='counts'
    ncfile.variables['ei2'].long_name='beam 1 echo intensity'
    
    ncfile.variables['ei3'][:]=ei3
    ncfile.variables['ei3'].units='counts'
    ncfile.variables['ei3'].long_name='beam 1 echo intensity'
    
    ncfile.variables['ei4'][:]=ei4
    ncfile.variables['ei4'].units='counts'
    ncfile.variables['ei4'].long_name='beam 1 echo intensity'
            
            
    
#    
    ncfile.close()
    
    print 'FINISHED'
        
    
    
if __name__ == "__main__":
    
    parser = optparse.OptionParser()
    parser.add_option('-m', '--mooring',dest='mooring',help='CP03ISSM:CP04OSSM:CP02PMCI:CP02PMCO:CP02PMUI:CP02PMUO:CP01CNSM',default='CP03ISSM:CP04OSSM:CP02PMCI:CP02PMCO:CP02PMUI:CP02PMUO:CP01CNSM',type='str')
    (opts, args) = parser.parse_args()
    
    
    print 'RUNNING'
    main(sys.argv)
