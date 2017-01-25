#!/usr/bin/env python
#

import os,sys
import glob,optparse
import numpy as np
import matplotlib,netCDF4
import matplotlib.pyplot as plt
import datetime
import struct
#
rtime=datetime.datetime(2013,01,01,00,00,00)
odir='/home/om/cron/pioneer/adcp/tel/'
mlat={"CP03ISSM":39.94,"CP04OSSM":40.36,"CP01CNSM":40.1332} 
mlon={"CP03ISSM":-70.88,"CP04OSSM":-70.88,"CP01CNSM":-70.8884}
bcut={"CP03ISSM":70,"CP04OSSM":300,"CP01CNSM":100}

mbin1={"CP02PMCI":9.05,"CP02PMCO":9.05, "CP02PMUI":9.05,"CP02PMUO":17.11}
mbinsize={"CP02PMCI":4,"CP02PMCO":4, "CP02PMUI":4,"CP02PMUO":8}

def main(argv):
 
    print opts.mooring    
    moorlist=opts.mooring.split(':')
    for [im, moor] in enumerate(moorlist):
        print moor
#        filelist=glob.glob(odir+moor+'/'+'*adcp.log') 
#        filelist.sort()
        for n in range(20):
            
            DEP='D%5.5d' % n
            filelist=glob.glob(odir+moor+'/'+DEP+'_'+'*adcp.log') 
            filelist.sort()
            ofile=odir+'PIONEER_ADCP_TELEMETERED_'+moor+'_'+DEP+'.nc'
            if not filelist:
                print moor+' - '+DEP+' - NO FILES'
            else:
                read_write_PD8(moor,filelist,ofile)
    
def read_write_PD8(moor,filelist,ncofile):
    print 'PROCESSING_ADCP'  
    time=np.array([])    
    pressure=np.array([]) 
    pitch=np.array([]) 
    roll=np.array([]) 
    heading=np.array([]) 
    temp=np.array([]) 
#        
    u=np.array([]) 
    v=np.array([]) 
    w=np.array([])
    err=np.array([]) 
    print 'creating arrays'
    nens=100000
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
    
    lat=mlat[moor]
    lon=mlon[moor]
#        
    count=0
    for fil in filelist:
        print fil
        with open(fil,'rb') as f:
            flag=False
            flag2=False
            ens=[]

            for line in f:
    
                data=line.split()
                
                if flag:

                    if 'Hdg:' in line:
                        ens.append(data)   
                        continue            
                    if 'Temp:' in line:
                        ens.append(data)
                        continue
                    if 'Bin' in line:
                        ens.append(data)                        
                        flag2=True
                        continue
                    
                    if flag2 and data[2]=='%d' % bind:
                      #  if int(data[2])==bind:
                      
                          ens.append(data)
                          bind=bind+1
                          
                          
                          
                    else:
                        pdata=parse_ens(ens)#                            
                        time[count]=pdata['ttime']
                        pressure[count]=0.0
                        pitch[count]=pdata['tpitch']
                        roll[count]=pdata['troll']
                        temp[count]=pdata['ttemp']
                        heading[count]=pdata['theading']
                        u[count,0:pdata['bins']]=pdata['tu']
                        v[count,0:pdata['bins']]=pdata['tv']
                        w[count,0:pdata['bins']]=pdata['tw']
                        err[count,0:pdata['bins']]=pdata['terr']
                        count=count+1
                        flag2=False
                        flag=False
                        continue
#                              
                      
                        

#                            print ens
#                            
##                            print len(pdata['tu'])
##                            print pdata['bins']
#                            time[count]=pdata['ttime']
#                            pressure[count]=0.0
#                            pitch[count]=pdata['tpitch']
#                            roll[count]=pdata['troll']
#                            temp[count]=pdata['ttemp']
#                            heading[count]=pdata['theading']
#                            u[count,0:pdata['bins']]=pdata['tu']
#                            v[count,0:pdata['bins']]=pdata['tv']
#                            w[count,0:pdata['bins']]=pdata['tw']
#                            err[count,0:pdata['bins']]=pdata['terr']
#                            count=count+1
#                            flag2=False
#                            flag=False
                else:
                    try:
                        
                        datetime.datetime.strptime(data[2],'%Y/%m/%d')               
                    
                        ens=[]
                        ens.append(data)
                        flag=True
                        bind=1
                    except:
                        continue
                            
                            
    print time.min(),time.max()
    
    plt.figure(1)
    plt.plot(time,u, 'ro')           
    plt.show()            

def parse_ens(ens):
    data={}
    print datetime.datetime.strptime(ens[0][2]+' '+ens[0][3],'%Y/%m/%d %H:%M:%S.%f') 
    tmp=datetime.datetime.strptime(ens[0][2]+' '+ens[0][3],'%Y/%m/%d %H:%M:%S.%f') -rtime
    data['ttime']=tmp.days+tmp.seconds/86400.0
    data['theading']=ens[1][3]
    data['tpitch']=ens[1][5]
    data['troll']=ens[1][7]
    data['ttemp']=ens[2][3]
    tu=np.array([]);
    tv=np.array([]);
    tw=np.array([]);
    terr=np.array([]);    
    tei1=np.array([]);
    tei2=np.array([]);
    tei3=np.array([]);
    tei4=np.array([]);
    for luv in ens[4:]:
        tu=np.append(tu,luv[5])
        tv=np.append(tv,luv[6])
        tw=np.append(tw,luv[7])
        terr=np.append(terr,luv[8])
        print luv
        tei1=np.append(tei1,luv[9])
        tei2=np.append(tei2,luv[10])
        tei3=np.append(tei3,luv[11])
        tei4=np.append(tei4,luv[12])
    
    data['tu']=tu
    data['tv']=tv
    data['tw']=tw
    data['terr']=terr
    
    data['tei1']=tei1
    data['tei2']=tei2
    data['tei3']=tei3
    data['tei4']=tei4
    data['bins']=len(ens[4:])
    return data

#        
#        ens=[]  
#        for [ind,tmp1] in enumerate(dat):
#            if hex(dat[ind])=='0x6e' and hex(dat[ind+1]) =='0x7f':
#                a=buffer(dat,ind+2,2)
#                nbytes=struct.unpack("h",a)[0]
#                startens=(ind)
#                try:                
#                    tdat=dat[startens:startens+nbytes+2]                
#                    a=buffer(tdat,nbytes,2)
#                    chksum=struct.unpack("<H",a)[0]
#                except:
#                    print 'ERROR'
#                    continue
#                if (sum(tdat[:nbytes]) & 65535) ==  chksum:
#                    ens.append(ind)
##        for [ind,tmp1] in enumerate(dat):
#         
#            tmp2=hex(tmp1)
#            if tmp2=='0x6e':
#                tmp3=hex(dat[ind+1])
#                if tmp3=='0x7f':
#                    
#                    ens.append(ind)
#                    
#
#        
#        for estart in ens:
#            
#            a=buffer(dat,estart+11,2)
#            year=struct.unpack("h",a)[0]
#            a=buffer(dat,estart+13,1)
#            month=struct.unpack("b",a)[0]
#            a=buffer(dat,estart+14,1)
#            day=struct.unpack("b",a)[0]
#            a=buffer(dat,estart+15,1)
#            hour=struct.unpack("b",a)[0]
#            a=buffer(dat,estart+16,1)
#            minute=struct.unpack("b",a)[0]
#            a=buffer(dat,estart+17,1)
#            sec=struct.unpack("b",a)[0]
#            a=buffer(dat,estart+18,1)
#            hsec=struct.unpack("b",a)[0]
#            sec=sec+(hsec/100)
##            print [year, month,day,hour,minute,sec]            
#            ttime=datetime.datetime(year, month,day,hour,minute,sec)-rtime
#            
#            a=buffer(dat,estart+19,2)
#            theading=struct.unpack("H",a)[0]
#            theading=theading/100.0
#            a=buffer(dat,estart+21,2)
#            tpitch=struct.unpack("h",a)[0]
#            tpitch=tpitch/100.0
#            a=buffer(dat,estart+23,2)
#            troll=struct.unpack("h",a)[0]
#            troll=troll/100.0
#            a=buffer(dat,estart+25,2)
#            ttemp=struct.unpack("h",a)[0]
#            ttemp=ttemp/100.0
#            a=buffer(dat,estart+27,4)
#            tpressure=struct.unpack("i",a)[0]
#            tpressure=tpressure*0.001
##            print pressure
#            
#            
#            a=buffer(dat,estart+33,1)
#            nbin=struct.unpack("b",a)[0]
#
#            nel=nbin*4*2
#            uv=np.array([])
#            for ind in range(0,nel,2):
#                a=buffer(dat,estart+34+ind,2)
#                tmp=struct.unpack("h",a)[0]
#                uv=np.append(uv,np.array(tmp))
#                
#            uv.shape=(4,nbin)
##        
##            time=np.append(time,ttime.days+ttime.seconds/86400.0)
##            pressure=np.append(pressure,tpressure)
##            pitch=np.append(pitch,tpitch)
##            roll=np.append(roll,troll)
##            temp=np.append(temp,ttemp)
##            heading=np.append(heading,theading)
##            uv=uv.transpose() 
##            u=np.concatenate((u,uv[:,0]))
##            v=np.concatenate((v,uv[:,1]))
##            w=np.concatenate((w,uv[:,2]))
##            err=np.concatenate((err,uv[:,3]))
##            
#            time[count]=ttime.days+ttime.seconds/86400.0
#            pressure[count]=tpressure
#            pitch[count]=tpitch
#            roll[count]=troll
#            temp[count]=ttemp
#            heading[count]=theading
#            u[count,0:nbin]=uv[0,:]
#            v[count,0:nbin]=uv[1,:]
#            w[count,0:nbin]=uv[2,:]
#            err[count,0:nbin]=uv[3,:]
#            
#            count=count+1            
            
#    print count        
#    print pressure 
##    print u.shape
#    time=time[0:count]
#    pressure=pressure[0:count]
#    pitch=pitch[0:count]
#    roll=roll[0:count]
#    temp=temp[0:count]
#    heading=heading[0:count]
#    u=u[0:count,0:nbin]
#    v=v[0:count,0:nbin]
#    w=w[0:count,0:nbin]
#    err=err[0:count,0:nbin]
#
#    ang=np.exp(1j*14.0*np.pi/180.0)
##
#    wc=u+1j*v
#    wc=wc*ang
#    u=wc.real
#    v=wc.imag        
#         
#    binsize=mbinsize[moor]
#    bin1=mbin1[moor]
#    bins=(np.array(range(nbin))*binsize)+bin1
#    xv, yv = np.meshgrid(pressure, bins)
#    xv=xv.transpose()
#    yv=yv.transpose() 
#    u[yv>xv*0.85]=np.nan
#    v[yv>xv*0.85]=np.nan
#    w[yv>xv*0.85]=np.nan
#    err[yv>xv*0.85]=np.nan
#    #  Depth CUTOFF
#    Ibad=np.where(pressure<bcut[moor])
#    mask=np.ones(len(time),dtype=bool)
#    mask[Ibad]=False
#    time=time[mask]        
#    pressure=pressure[mask]
#    heading=heading[mask]
#    pitch=pitch[mask]
#    roll=roll[mask]
#    temp=temp[mask]
#    u=u[mask,:]
#    v=v[mask,:]
#    w=w[mask,:]
#    err=err[mask,:]
#    
#    Is = np.argsort(time)
#    time=time[Is]        
#    pressure=pressure[Is]
#    heading=heading[Is]
#    pitch=pitch[Is]
#    roll=roll[Is]
#    temp=temp[Is]
#    u=u[Is,:]
#    v=v[Is,:]
#    w=w[Is,:]
#    err=err[Is,:]
#    
#    
##  
##            
###             
####      
##    plt.figure(1)
##    plt.plot(time,pressure, 'ro')
####  
##    plt.figure(2)
##    plt.plot(time,heading, 'ro')
####        
###    plt.figure(3)
###    plt.pcolor(time,bins,u.transpose(),vmin=-500, vmax=500)
###    
##    plt.show()
###        
##    
##
#    ncfile = netCDF4.Dataset(ncofile, 'w', format='NETCDF4')
#    ncfile.Conventions= "CF-1.6"
##    
##    
#    ncfile.createDimension('time', None)
#    ncfile.createDimension('depth', nbin)
#    ncfile.createDimension('lat', 1) 
#    ncfile.createDimension('lon', 1)
#    ncfile.createVariable('time','f8',('time',))
#    ncfile.createVariable('heading','f8',('time',))
#    ncfile.createVariable('pressure','f8',('time',))
#    ncfile.createVariable('pitch','f8',('time',))
#    ncfile.createVariable('roll','f8',('time',))
#    ncfile.createVariable('temperature','f8',('time',))
#    ncfile.createVariable('range','f8',('depth',))
#    ncfile.createVariable('latitude','f8',('lat',))
#    ncfile.createVariable('longitude','f8',('lon',))
#    
#    ncfile.createVariable('u','f8',('time','depth'))
#    ncfile.createVariable('v','f8',('time','depth'))
#    ncfile.createVariable('w','f8',('time','depth'))
#    ncfile.createVariable('err','f8',('time','depth'))
##        
#
#    ncfile.variables['time'][:]=time
#    ncfile.variables['time'].units='days since 2013-01-01 00:00:00'
#    ncfile.variables['time'].long_name='time'
#    ncfile.variables['time'].standard_name='time'
#
#    
#    ncfile.variables['latitude'][:]=lat
#    ncfile.variables['latitude'].units='degrees_north'
#    ncfile.variables['latitude'].long_name='Latitude'
#    ncfile.variables['latitude'].standard_name='latitude'
#    
#    
#    
#    ncfile.variables['longitude'][:]=lon
#    ncfile.variables['longitude'].units='degrees_east'
#    ncfile.variables['longitude'].long_name='Longitude'
#    ncfile.variables['longitude'].standard_name='longitude'
#    
#    ncfile.variables['range'][:]=bins
#    ncfile.variables['range'].units='m'
#    ncfile.variables['range'].long_name='range from ADCP'
#    ncfile.variables['range'].standard_name='depth'
##    
#    ncfile.variables['pressure'][:]=pressure
#    ncfile.variables['pressure'].units='dbar'
#    ncfile.variables['pressure'].long_name='Pressure'
#    ncfile.variables['pressure'].standard_name='sea_water_pressure'
#
##        
#    ncfile.variables['heading'][:]=heading
#    ncfile.variables['heading'].units='degrees'
#    ncfile.variables['heading'].long_name='heading'
##    
#
#    ncfile.variables['temperature'][:]=temp
#    ncfile.variables['temperature'].units='degrees C'
#    ncfile.variables['temperature'].long_name='temperature'
##    
#    ncfile.variables['pitch'][:]=pitch
#    ncfile.variables['pitch'].units='degrees'
#    ncfile.variables['pitch'].long_name='pitch'
#
#    ncfile.variables['roll'][:]=roll
#    ncfile.variables['roll'].units='degrees'
#    ncfile.variables['roll'].long_name='roll'
#
#    ncfile.variables['u'][:]=u/1000.0
#    ncfile.variables['u'].units='m s-1'
#    ncfile.variables['u'].long_name='eastward water velocity'
#    ncfile.variables['u'].standard_name='eastward_sea_water_velocity'
#
#    ncfile.variables['v'][:]=v/1000.0
#    ncfile.variables['v'].units='m s-1'
#    ncfile.variables['v'].long_name='northward water velocity'
#    ncfile.variables['v'].standard_name='northward_sea_water_velocity'
#
#    ncfile.variables['w'][:]=w/1000.0
#    ncfile.variables['w'].units='m s-1'
#    ncfile.variables['w'].long_name='vertical water velocity'
#    ncfile.variables['w'].standard_name='upward_sea_water_velocity'
#
#    ncfile.variables['err'][:]=err/1000.0
#    ncfile.variables['err'].units='m s-1'
#    ncfile.variables['err'].long_name='error water velocity'
##    
##    
##        ncfile.variables['ei1'][:]=ei1
##        ncfile.variables['ei1'].units='counts'
##        ncfile.variables['ei1'].long_name='beam 1 echo intensity'
##    
##        ncfile.variables['ei2'][:]=ei2
##        ncfile.variables['ei2'].units='counts'
##        ncfile.variables['ei2'].long_name='beam 1 echo intensity'
##    
##        ncfile.variables['ei3'][:]=ei3
##        ncfile.variables['ei3'].units='counts'
##        ncfile.variables['ei3'].long_name='beam 1 echo intensity'
##    
##        ncfile.variables['ei4'][:]=ei4
##        ncfile.variables['ei4'].units='counts'
##        ncfile.variables['ei4'].long_name='beam 1 echo intensity'
##            
##            
##    
##    
#    ncfile.close()
#    
#    print 'FINISHED'
        
    
    
if __name__ == "__main__":

     
    parser = optparse.OptionParser()
    parser.add_option('-m', '--mooring',dest='mooring',help='CP03ISSM:CP04OSSM:CP01CNSM',default='CP03ISSM:CP04OSSM:CP01CNSM',type='str')
    (opts, args) = parser.parse_args()
    
    
    print 'RUNNING'
    main(sys.argv)
