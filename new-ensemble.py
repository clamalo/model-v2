import xarray as xr
import os
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.colors as colors
import cartopy
from metpy.plots import USCOUNTIES
import requests
from datetime import datetime,timedelta
from matplotlib import cm 
from matplotlib.colors import ListedColormap,LinearSegmentedColormap
from ecmwf.opendata import Client
from urllib.request import urlopen
from bs4 import BeautifulSoup
from tzwhere import tzwhere
from dateutil import tz as dateutil
tz = tzwhere.tzwhere()
from_zone = dateutil.gettz('UTC')

def name_member(member):
    if int(member) < 10:
        member = '0'+str(member)
    else:
        member = str(member)
    return member

def hourly_snow_colormap():
    # cmap = colors.ListedColormap(['#FFFFFF','#cccccc', '#666666', '#7fb2ff', '#1933b2', '#7fff7f', '#0c660c', '#ffff66', '#a51900', '#ff99ff', '#660766', '#666666'])
    cmap = colors.ListedColormap(['#FFFFFF', '#cccccc', '#7fb2ff', '#1933b2', '#7fff7f', '#0c660c', '#ffff66', '#a51900', '#ff99ff', '#660766', '#666666'])
    return cmap

def total_snow_colormap():
    cmap = colors.ListedColormap(['#FFFFFF','#7fb2ff','#4c72d8','#1933b2','#7fff7f','#46b246','#0c660c','#ffff66','#e1b244','#c36622','#a51900','#ff99ff','#cc68cc','#993899','#660766','#cccccc','#999999','#666666'])
    return cmap

def hourly_precip_colormap():
    cmap = colors.ListedColormap(['#ffffff', '#bdbfbd','#aba5a5', '#838383', '#6e6e6e', '#b5fbab', '#95f58b','#78f572', '#50f150','#1eb51e', '#0ea10e', '#1464d3'])
    return cmap

def total_precip_colormap():
    cmap = colors.ListedColormap(['#ffffff','#cccccc','#7fff00','#3fcc00','#009900','#0f4c8c','#0a7faa','#05b2c7','#00e5e5','#8c66cc','#8c33ac','#8c008c','#8c0000','#cc0000','#e53f00','#ff7f00','#cc8c00','#e5c500','#ffa5bf'])
    return cmap

def temp_colormap():
    cmap = colors.ListedColormap(['#ffffff','#7f1786','#8634e5','#8469c7','#ea33f7','#3c8925','#5dca3b','#a0fc4e','#75fb4c','#0000f5','#458ef7','#4fafe8','#6deaec','#75fbfd','#ffff54','#eeee4e','#f9d949','#f2a95f','#ef8955','#ef8632','#fbe5dd','#f3b1ba','#ed736f','#db4138','#dc4f25','#ea3323','#bc271a','#c3882e','#824b2d','#7f170e'])
    return cmap

def slr_colormap():
    cmap = colors.ListedColormap(['#ffffff','#afeeee','#81a7e8','#5b6ce1','#4141de','#4b0082','#611192','#7722a2','#8e33b3','#a444c3','#ba55d3','#da70d6','#d452bb','#cd33a0','#c71585','#d24081','#de6b7e','#e9967a','#f0b498','#f8d1b7'])
    return cmap

def total_opensnow_colormap():
    cmap = colors.ListedColormap(['#ffffff','#dccfff','#c6afff','#9247ff','#7000ff','#5700ff','#a9ffc0','#00ff13','#008e05','#b7ce00','#f4ff00','#ffcf94','#ff7900','#ff0000','#890000','#ff6c77','#ff02fe','#8e007f'])
    return cmap

def weatherbell_precip_colormap():
    cmap = colors.ListedColormap(['#ffffff', '#bdbfbd','#aba5a5', '#838383', '#6e6e6e', '#b5fbab', '#95f58b','#78f572', '#50f150','#1eb51e', '#0ea10e', '#1464d3', '#2883f1', '#50a5f5','#97d3fb', '#b5f1fb','#fffbab', '#ffe978', '#ffc13c', '#ffa100', '#ff6000','#ff3200', '#e11400','#c10000', '#a50000', '#870000', '#643c31', '#8d6558','#b58d83', '#c7a095','#f1ddd3', '#cecbdc'])#, '#aca0c7', '#9b89bd', '#725ca3','#695294', '#770077','#8d008d', '#b200b2', '#c400c4', '#db00db'])
    return cmap

def ptype_colormap():
    # cmap = colors.ListedColormap(['#ffffff', '#45f248', '#FFDA00', '#29b6f6'])
    white_cmap = colors.ListedColormap(['#ffffff','#ffffff','#ffffff','#ffffff','#ffffff'])
    rain_cmap = colors.ListedColormap(['#b5e5ad','#76c77c','#56c164','#3cb15c','#319f4f'])
    # rain_cmap = cm.get_cmap('Greens',10)
    mixed_cmap = colors.ListedColormap(['#fab87d','#fec067','#ffa772','#f69b55','#ff892e'])
    snow_cmap = colors.ListedColormap(['#b3cbe5','#919bcd','#8f85bd','#8d6ab5','#8b54a5'])
    snow_cmap = cm.get_cmap('seismic_r',10)
    cmap = np.vstack((white_cmap(np.linspace(0,1,5)),rain_cmap(np.linspace(0,1,5)),mixed_cmap(np.linspace(0,1,5)),snow_cmap(np.linspace(0,1,10))[5:]))
    cmap = ListedColormap(cmap, name='ptype')
    return cmap

def euro_processing(f):

    chelsa_ds = xr.open_dataset('/Users/clamalo/documents/11_chelsa0.4.nc')
    temp_chelsa_ds = xr.open_dataset('/Users/clamalo/documents/temp_11_chelsa0.4.nc')
    chelsa_ds = chelsa_ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))
    temp_chelsa_ds = temp_chelsa_ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

    ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/ecmwf_'+name_frame(f)+'.grib',engine='cfgrib')
    ds = ds.mean(dim='number')
    prior_ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/ecmwf_'+name_frame(f-3)+'.grib',engine='cfgrib')
    prior_ds = prior_ds.mean(dim='number')
    ds['tp'] = ds['tp']-prior_ds['tp']
    ds['t2m_avg'] = ds['t2m'].copy()
    ds['t2m_avg'] = (ds['t2m_avg'] + prior_ds['t2m'])/2
    ds['longitude'] = (ds['longitude'] + 180) % 360 - 180

    ds = ds.interp(latitude=chelsa_ds['lat'],longitude=chelsa_ds['lon'])

    ds['tp'] = ds['tp']*39.3701
    ds['tp'] = ds['tp']*chelsa_ds['precip']
    ds['t2m'] = ds['t2m']*temp_chelsa_ds['tas']
    ds['t2m_avg'] = ds['t2m_avg']*temp_chelsa_ds['tas']
    return ds


def gefs_processing(f):

    chelsa_ds = xr.open_dataset('/Users/clamalo/documents/11_chelsa0.25.nc')
    temp_chelsa_ds = xr.open_dataset('/Users/clamalo/documents/temp_11_chelsa0.25.nc')
    chelsa_ds = chelsa_ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))
    temp_chelsa_ds = temp_chelsa_ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

    ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(f)+'.grib2')

    prior_ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(f-3)+'.grib2')

    if (f-3)%6 != 0:
        ds['tp'] = ds['tp'] - prior_ds['tp']

    ds['t2m_avg'] = ds['t2m'].copy()
    ds['t2m_avg'] = (ds['t2m_avg'] + prior_ds['t2m'])/2

    ds['longitude'] = (ds['longitude'] + 180) % 360 - 180

    ds = ds.interp(latitude=chelsa_ds['lat'],longitude=chelsa_ds['lon'])

    ds['tp'] = ds['tp']*.0393701
    ds['tp'] = ds['tp']*chelsa_ds['precip']
    ds['t2m'] = ds['t2m']*temp_chelsa_ds['tas']
    ds['t2m_avg'] = ds['t2m_avg']*temp_chelsa_ds['tas']
    return ds

def find_temperature(gh1,gh2,avg,elevation):
    if avg == False:
        temperature = gh1['t'] + (gh2['t'] - gh1['t']) * ((elevation - gh1['gh']) / (gh2['gh'] - gh1['gh']))
    else:
        temperature = gh1['t_avg'] + (gh2['t_avg'] - gh1['t_avg']) * ((elevation - gh1['gh_avg']) / (gh2['gh_avg'] - gh1['gh_avg']))
    return temperature

def name_frame(frame):
    if int(frame) < 10:
        frame = '00' + str(frame)
    elif int(frame) < 100:
        frame = '0'+str(frame)
    else:
        frame = str(frame)
    return frame

def interpolate(ds,interp_factor):
    new_lon = np.linspace(ds.lon[0], ds.lon[-1], ds.dims["lon"] * interp_factor)
    new_lat = np.linspace(ds.lat[0], ds.lat[-1], ds.dims["lat"] * interp_factor)
    ds = ds.interp(lat=new_lat, lon=new_lon)
    return ds

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def datestr_and_cycle():
    return '20221028', '18'

def ingest_frame(frame,day_diff,datestr,cycle):

    # client = Client("ecmwf", beta=True)
    # parameters = ['2t','tp']
    # filename = '/Users/clamalo/documents/ensemble-blend/gribs/ecmwf_'+name_frame(frame)+'.grib'

    # client.retrieve(
    # date=day_diff,
    # time=int(cycle),
    # step=frame,
    # stream="enfo",
    # type="pf",
    # levtype="sfc",
    # param=parameters,
    # target=filename
    # )

    idx_url = 'https://noaa-gefs-pds.s3.amazonaws.com/gefs.'+datestr+'/'+cycle+'/atmos/pgrb2sp25/geavg.t'+cycle+'z.pgrb2s.0p25.f'+name_frame(frame)+'.idx'
    os.system('wget '+idx_url+' -P /Users/clamalo/documents/ensemble-blend/')

    idx_file = '/Users/clamalo/documents/ensemble-blend/geavg.t'+cycle+'z.pgrb2s.0p25.f'+name_frame(frame)+'.idx'
    with open(idx_file, 'r') as f:
        lines = f.readlines()

    #find closest multiple of 6 to frame
    if frame % 6 == 0:
        closest_multiple = frame-6
    else:
        closest_multiple = frame - (frame % 6)

    variables = ['APCP:surface:'+str(closest_multiple)+'-'+str(frame)+' hour acc fcst','TMP:2 m above ground:'+str(frame)+' hour fcst']
    if frame == 0:
        variables = ['TMP:2 m above ground:anl']
    for variable in variables:
        for l in range(len(lines)):
            if lines[l].split(':')[3]+':'+lines[l].split(':')[4]+':'+lines[l].split(':')[5] == variable:
                start_bytes = int(lines[l].split(':')[1])
                end_bytes = int(lines[l+1].split(':')[1])

                grib_url = 'https://noaa-gefs-pds.s3.amazonaws.com/gefs.'+datestr+'/'+cycle+'/atmos/pgrb2sp25/geavg.t'+cycle+'z.pgrb2s.0p25.f'+name_frame(frame)

                if frame!=0:
                    if 'APCP' in variable:
                        os.system('curl -r '+str(start_bytes)+'-'+str(end_bytes)+' '+grib_url+' > /Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(frame)+'.grib2')
                    else:
                        os.system('curl -r '+str(start_bytes)+'-'+str(end_bytes)+' '+grib_url+' >> /Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(frame)+'.grib2')
                else:
                    os.system('curl -r '+str(start_bytes)+'-'+str(end_bytes)+' '+grib_url+' > /Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(frame)+'.grib2')

    os.remove(idx_file)

    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?file=geavg.t'+cycle+'z.pgrb2a.0p50.f'+name_frame(frame)+'&lev_1000_mb=on&lev_2_m_above_ground=on&lev_500_mb=on&lev_700_mb=on&lev_850_mb=on&lev_925_mb=on&lev_surface=on&var_HGT=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.'+datestr+'%2F'+cycle+'%2Fatmos%2Fpgrb2ap5'
    response = requests.get(url)
    with open('/Users/clamalo/documents/ensemble-blend/gribs/gefs_air_'+name_frame(frame)+'.grib2', 'wb') as file:
        file.write(response.content)




def plot_hourly_snow(ds,f,points,domains):
    global forecast_datestr
    base_datestr = datestr+cycle
    base_date = datetime.strptime(base_datestr,'%Y%m%d%H')
    forecast_date = base_date + timedelta(hours=f)
    forecast_datestr = forecast_date.strftime('%Y%m%d%H')
    forecast_datestr = forecast_datestr[4:6]+'/'+forecast_datestr[6:8]+' '+forecast_datestr[8:10]+'z'

    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        # ds['snow'] = ds['snow']*.0393701
        max_value = round(np.max(domain_ds['snow'].values.flatten()),2)

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('3-Hourly Snowfall (Inches) - Forecast Hour '+str(f)+' ('+forecast_datestr+') - Max: '+str(max_value)+'"',fontsize=12)
        colormap = hourly_snow_colormap()
        # bounds = [0,0.01,0.25,0.5,0.75,1,1.5,2,2.5,3,3.5,4]
        bounds = [0,0.1,0.5,0.75,1,1.5,2,2.5,3,3.5,4]
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
        # cf = ax.pcolormesh(ds['longitude'],ds['latitude'],ds['snow'], norm=norm, cmap=colormap)
        cf = ax.contourf(domain_ds['lon'],domain_ds['lat'],domain_ds['snow'], levels=bounds, norm=norm, cmap=colormap)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        # ax.add_feature(cartopy.feature.LAKES,linewidth=0.5,edgecolor='black',facecolor='white')
        # cbar = plt.colorbar(cf,ax=ax)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks(bounds)
        # cbar.set_ticklabels(['0','0.01','0.25','0.5','0.75','1','1.5','2','2.5','3','3.5','4'])
        cbar.set_ticklabels(['0','0.1','0.5','0.75','1','1.5','2','2.5','3','3.5','4'])
        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/snow/'+str(f)+'_snow.png',dpi=200,bbox_inches='tight')

    for n in range(len(points)):
        lat,lon = float(points[n][1]),float(points[n][2])
        value = float(ds['snow'].sel(lat=lat,lon=lon,method='nearest').values)
        if value < 0:
            value = 0
        points[n][5].append(value)

    return points

def plot_total_snow(ds,f,points,domains):
    # ds['snow'] = ds['snow']*.0393701
    # max_value = round(np.max(ds['total_snow'].values.flatten()),2)

    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        max_value = round(np.max(domain_ds['snow'].values.flatten()),2)

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('Total Snowfall (Inches) - Forecast Hour '+str(f)+' ('+forecast_datestr+') - Max: '+str(max_value)+'"',fontsize=12)
        colormap = total_snow_colormap()
        # colormap = total_opensnow_colormap()
        bounds = [0,1,2,4,6,8,10,12,15,18,21,24,27,30,33,36,42,48]
        # bounds = [0,2,4,8,12,16,20,24,30,36,42,48,54,60,66,72,84,96]
        # bounds = [0,0.1,0.2,0.5,1,2,3,4,5,6,7,8,9,10,15,20,25,30,40]
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
        # cf = ax.pcolormesh(ds['longitude'],ds['latitude'],ds['snow'], norm=norm, cmap=colormap)
        cf = ax.contourf(domain_ds['lon'],domain_ds['lat'],domain_ds['snow'], levels=bounds, norm=norm, cmap=colormap)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        # cbar = plt.colorbar(cf,ax=ax)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks(bounds)
        cbar.set_ticklabels(['0','1','2','4','6','8','10','12','15','18','21','24','27','30','33','36','42','48'])
        # cbar.set_ticklabels(['0','2','4','8','12','16','20','24','30','36','42','48','54','60','66','72','84','96'])

        lat,lon = 39.33430, -120.16520
        # lon-=360
        print('Value at '+str(lat)+','+str(lon)+': '+str(domain_ds['snow'].sel(lat=lat,lon=lon,method='nearest').values))
        # ax.scatter(lon,lat,transform=ccrs.PlateCarree(),color='black',s=2)

        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/total_snow/'+str(f)+'_total_snow.png',dpi=200,bbox_inches='tight')

    for n in range(len(points)):
        lat,lon = float(points[n][1]),float(points[n][2])
        value = float(ds['snow'].sel(lat=lat,lon=lon,method='nearest').values)
        if value < 0:
            value = 0
        points[n][6].append(value)

    return points

def plot_hourly_precip(ds,f,points,domains):
    # ds['tp'] = ds['tp']*.0393701

    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        max_value = round(np.max(domain_ds['tp'].values.flatten()),2)

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('3-Hourly Precipitation (Inches) - Forecast Hour '+str(f)+' ('+forecast_datestr+') - Max: '+str(max_value)+'"',fontsize=12)
        colormap = hourly_precip_colormap()
        bounds = [0,0.01,0.03,0.05,0.075,0.1,0.15,0.2,0.25,0.3,0.4,0.5]
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
        # cf = ax.pcolormesh(ds['longitude'],ds['latitude'],ds['tp'], norm=norm, cmap=colormap)
        cf = ax.contourf(domain_ds['longitude'],domain_ds['latitude'],domain_ds['tp'], levels=bounds, norm=norm, cmap=colormap)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        # cbar = plt.colorbar(cf,ax=ax)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks(bounds)
        cbar.set_ticklabels(['0','0.01','0.03','0.05','0.075','0.1','0.15','0.2','0.25','0.3','0.4','0.5'])
        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/qpf/'+str(f)+'_qpf.png',dpi=200,bbox_inches='tight')

    for n in range(len(points)):
        lat,lon = float(points[n][1]),float(points[n][2])
        value = float(ds['tp'].sel(lat=lat,lon=lon,method='nearest').values)
        if value < 0:
            value = 0
        points[n][7].append(value)

    return points

def plot_total_precip(ds,f,points,domains):
    # ds['tp'] = ds['tp']*.0393701
    # max_value = round(np.max(ds['total_precip'].values.flatten()),2)

    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        max_value = round(np.max(domain_ds['tp'].values.flatten()),2)

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('Total Precipitation (Inches) - Forecast Hour '+str(f)+' ('+forecast_datestr+') - Max: '+str(max_value)+'"',fontsize=12)
        colormap = weatherbell_precip_colormap()
        # bounds = [0,0.01,0.05,0.1,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.5,3,4,5,7,10,15,20]
        bounds = [0,0.01,0.03,0.05,0.075,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.2,1.4,1.6,1.8,2,2.5,3,3.5,4,5,6,7,8,9,10]#,11,12,13,14,15,16,17,18,19,20])
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
        # cf = ax.pcolormesh(ds['longitude'],ds['latitude'],ds['tp'], norm=norm, cmap=colormap)
        cf = ax.contourf(domain_ds['longitude'],domain_ds['latitude'],domain_ds['tp'], levels=bounds, norm=norm, cmap=colormap)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        # cbar = plt.colorbar(cf,ax=ax)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks([0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.2, 1.6, 2, 3, 4, 6, 8, 10])
        cbar.set_ticklabels(['0.01', '0.05', '0.1', '0.2', '0.3', '0.5', '0.7', '0.9', '1.2', '1.6', '2', '3', '4', '6', '8', '10'])
        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/total_qpf/'+str(f)+'_total_qpf.png',dpi=200,bbox_inches='tight')

    for n in range(len(points)):
        lat,lon = float(points[n][1]),float(points[n][2])
        value = float(ds['tp'].sel(lat=lat,lon=lon,method='nearest').values)
        if value < 0:
            value = 0
        points[n][8].append(value)

    return points

def plot_temperature(ds,f,points,domains):
    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        max_value = round(np.max(domain_ds['t2m'].values.flatten()),2)
        min_value = round(np.min(domain_ds['t2m'].values.flatten()),2)

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('Temperature (F) - Forecast Hour '+str(f)+' ('+forecast_datestr+') - Max: '+str(max_value)+'F, Min: '+str(min_value)+'F',fontsize=12)
        colormap = temp_colormap()
        bounds = [-100,-35,-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110]
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
        # cf = ax.pcolormesh(domain_ds['lon'],domain_ds['lat'],domain_ds['t2m'], norm=norm, cmap=colormap)
        cf = ax.contourf(domain_ds['lon'],domain_ds['lat'],domain_ds['t2m'], levels=bounds, norm=norm, cmap=colormap)
        cs = ax.contour(domain_ds['lon'],domain_ds['lat'],domain_ds['t2m'], levels=[32], colors='black', linewidths=0.4)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        # cbar = plt.colorbar(cf,ax=ax)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks(bounds[2:-1:2])
        # cbar.set_ticklabels(['-35','-30','-25','-20','-15','-10','-5','0','5','10','15','20','25','30','35','40','45','50','55','60','65','70','75','80','85','90','95','100','105','110'])
        cbar.set_ticklabels(['-30','-20','-10','0','10','20','30','40','50','60','70','80','90','100'])
        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/temp/'+str(f)+'_temp.png',dpi=200,bbox_inches='tight')

    for n in range(len(points)):
        lat,lon = float(points[n][1]),float(points[n][2])
        value = float(ds['t2m'].sel(lat=lat,lon=lon,method='nearest').values)
        points[n][9].append(value)

    return points

def plot_slr(ds,f,method,points,domains):
    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        max_value = round(np.max(domain_ds['slr'].values.flatten()),1)

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('SLR - Forecast Hour '+str(f)+' ('+forecast_datestr+') - Max: '+str(max_value)+':1',fontsize=12)
        colormap = slr_colormap()
        if method == 'kuchera':
            bounds = [0,3,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40]
        elif method == 'opensnow':
            bounds = [0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))
        # cf = ax.pcolormesh(ds['longitude'],ds['latitude'],ds['slr'], norm=norm, cmap=colormap)
        cf = ax.contourf(domain_ds['lon'],domain_ds['lat'],domain_ds['slr'], levels=bounds, norm=norm, cmap=colormap)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        # cbar = plt.colorbar(cf,ax=ax)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks(bounds)
        if method == 'kuchera':
            cbar.set_ticklabels(['0','3','4','6','8','10','12','14','16','18','20','22','24','26','28','30','32','34','36','38','40'])
        elif method == 'opensnow':
            cbar.set_ticklabels(['0','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20'])
        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/slr/'+str(f)+'_slr.png',dpi=200,bbox_inches='tight')

    for n in range(len(points)):
        lat,lon = float(points[n][1]),float(points[n][2])
        value = float(ds['slr'].sel(lat=lat,lon=lon,method='nearest').values)
        points[n][10].append(value)

    return points

def plot_ptype(ds,f,points,domains):

    for domain in domains:
        top_lat = domains[domain]['top_lat']
        bottom_lat = domains[domain]['bottom_lat']
        left_lon = domains[domain]['left_lon']
        right_lon = domains[domain]['right_lon']

        domain_ds = ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

        fig = plt.figure(figsize=(10,7))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.title('P-Type (0.1" QPF Increments) - Forecast Hour '+str(f)+' ('+forecast_datestr+')',fontsize=12)

        colormap = ptype_colormap()
        bounds = [0,1,2,3,4]
        bounds = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2]
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=len(bounds))

        cf = ax.contourf(domain_ds['lon'],domain_ds['lat'],domain_ds['ptype'], levels=bounds, norm=norm, cmap=colormap)
        ax.coastlines()
        ax.add_feature(cartopy.feature.STATES,linewidth=1)
        ax.add_feature(USCOUNTIES.with_scale('500k'),linewidth=0.075)
        cbar = plt.colorbar(cf, shrink=0.7, orientation="horizontal", pad=0.03)
        cbar.set_ticks([0.25,0.75,1.25,1.75])
        cbar.set_ticklabels(['None','Rain','Mixed','Snow'])
        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/'+str(domain)+'/ptype/'+str(f)+'_ptype.png',dpi=200,bbox_inches='tight')

    return points


for f in range(0,169,3):

    if f==0:
        #read html from points.html
        with open('/Users/clamalo/documents/points.html', 'r') as myfile:
            text=myfile.read()

        points = text.split(';')
        points.pop()
        for n in range(len(points)):
            if n == 0:
                points[n] = points[n].split('\n')[0]
            else:
                points[n] = points[n].split('\n')[1]

            points[n] = points[n].split(',')

        for n in range(len(points)-1,-1,-1):
            # if points[n][-1] != 'NorCal' and points[n][-1] != 'PNW' and points[n][-1] != 'Utah' and points[n][-1] != 'Colorado' and points[n][-1] != 'MT' and points[n][-1] != 'WY' and points[n][-1] != 'ID':
            # if points[n][-1] != 'Northeast':
            # if points[n][-1] != 'Colorado':
            if points[n][-1] != 'Utah' and points[n][-1] != 'Colorado' and points[n][-1] != 'PNW' and points[n][-1] != 'NorCal':
                points.pop(n)
            
        for n in range(len(points)):
            points[n].append([])
            points[n].append([])
            points[n].append([])
            points[n].append([])
            points[n].append([])
            points[n].append([])


    datestr,cycle = '20221122','18'

    datetime_datestr = datetime.strptime(datestr,'%Y%m%d')
    utcnow = datetime.strptime((str(datetime.utcnow().year)+str(datetime.utcnow().month)+str(datetime.utcnow().day)),'%Y%m%d')
    day_diff = (datetime_datestr - utcnow).days
    ingest_frame(f,day_diff,datestr,cycle)

    if f == 0:
        continue

    top_lat,left_lon = 50,-125
    bottom_lat,right_lon = 35,-65

    domains = {'PNW': {'top_lat': 50, 'left_lon': -125, 'bottom_lat': 42, 'right_lon': -111},
                'NorCal': {'top_lat': 42, 'left_lon': -125, 'bottom_lat': 36.5, 'right_lon': -115},
                'Utah-Colorado': {'top_lat': 42, 'left_lon': -113.5, 'bottom_lat': 37, 'right_lon': -104}}

    #make directory for each domain with subdirectories "ptype", "qpf", "slr", "temp", "snow", "total_snow", "total_qpf"
    for domain in domains:
        if not os.path.exists('/Users/clamalo/documents/ensemble-blend/images/'+domain):
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain)
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/ptype')
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/qpf')
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/slr')
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/temp')
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/snow')
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/total_snow')
            os.makedirs('/Users/clamalo/documents/ensemble-blend/images/'+domain+'/total_qpf')

    chelsa_ds = xr.open_dataset('/Users/clamalo/documents/11_chelsa0.25.nc')
    temp_chelsa_ds = xr.open_dataset('/Users/clamalo/documents/temp_11_chelsa0.25.nc')
    chelsa_ds = chelsa_ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))
    temp_chelsa_ds = temp_chelsa_ds.sel(lat=slice(bottom_lat,top_lat),lon=slice(left_lon,right_lon))

    ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(f)+'.grib2')

    prior_ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/gefs_'+name_frame(f-3)+'.grib2')

    if (f-3)%6 != 0:
        ds['tp'] = ds['tp'] - prior_ds['tp']
    ds['longitude'] = (ds['longitude'] + 180) % 360 - 180
    ds = ds.interp(latitude=chelsa_ds['lat'],longitude=chelsa_ds['lon'])

    air_ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/gefs_air_'+name_frame(f)+'.grib2',engine='cfgrib')
    prior_air_ds = xr.load_dataset('/Users/clamalo/documents/ensemble-blend/gribs/gefs_air_'+name_frame(f-3)+'.grib2',engine='cfgrib')

    air_ds['gh_avg'] = (air_ds['gh']+prior_air_ds['gh'])/2
    air_ds['t_avg'] = (air_ds['t']+prior_air_ds['t'])/2

    air_ds['longitude'] = (air_ds['longitude'] + 180) % 360 - 180
    air_ds = air_ds.interp(latitude=chelsa_ds['lat'],longitude=chelsa_ds['lon'])

    gh1 = air_ds.isel(isobaricInhPa=0)
    gh2 = air_ds.isel(isobaricInhPa=1)
    gh3 = air_ds.isel(isobaricInhPa=2)
    gh4 = air_ds.isel(isobaricInhPa=3)
    gh5 = air_ds.isel(isobaricInhPa=4)

    ds['tp'] = ds['tp']*chelsa_ds['precip']*.0393701

    if f == 3:
        elevation_ds = xr.open_dataset('/Users/clamalo/documents/elevation.nc')
        elevation_ds = elevation_ds.interp(lat=ds['lat'],lon=ds['lon'])
        elevation_ds = elevation_ds.fillna(0)

    ds['t2m'] = xr.where(elevation_ds['elevation'] < gh2['gh'], find_temperature(gh1,gh2,False,elevation_ds['elevation']), xr.where(elevation_ds['elevation'] < gh3['gh'], find_temperature(gh2,gh3,False,elevation_ds['elevation']), xr.where(elevation_ds['elevation'] < gh4['gh'], find_temperature(gh3,gh4,False,elevation_ds['elevation']),find_temperature(gh4,gh5,False,elevation_ds['elevation']))))
    # ds['t2m'] = xr.where(elevation_ds['elevation'] < gh1['gh'], ds['t2m'], xr.where(elevation_ds['elevation'] < gh2['gh'], find_temperature(gh1,gh2,elevation_ds['elevation']), xr.where(elevation_ds['elevation'] < gh3['gh'], find_temperature(gh2,gh3,elevation_ds['elevation']), xr.where(elevation_ds['elevation'] < gh4['gh'], find_temperature(gh3,gh4,elevation_ds['elevation']),find_temperature(gh4,gh5,elevation_ds['elevation'])))))
    ds['t2m_avg'] = xr.where(elevation_ds['elevation'] < gh2['gh'], find_temperature(gh1,gh2,True,elevation_ds['elevation']), xr.where(elevation_ds['elevation'] < gh3['gh'], find_temperature(gh2,gh3,True,elevation_ds['elevation']), xr.where(elevation_ds['elevation'] < gh4['gh'], find_temperature(gh3,gh4,True,elevation_ds['elevation']),find_temperature(gh4,gh5,True,elevation_ds['elevation']))))
    
    ds = interpolate(ds,3)

    ds['tp'] = ds['tp'].where(ds['tp'] > 0, 0)

    ds['slr'] = ds['t2m_avg'].copy()

    method = 'opensnow'
    if method == 'kuchera':
        ds['slr'] = xr.where(ds['t2m_avg'] < 271.16, 12+2*(271.16-ds['t2m_avg']), xr.where(ds['t2m_avg'] > 271.16, 12-2*(ds['t2m_avg']-271.16), 12))
        ds['t2m_avg'] = ds['t2m_avg'] * 9/5 - 459.67
        ds['t2m'] = ds['t2m'] * 9/5 - 459.67
    elif method == 'opensnow':
        ds['t2m_avg'] = ds['t2m_avg'] * 9/5 - 459.67
        ds['t2m'] = ds['t2m'] * 9/5 - 459.67
        ds['slr'] = xr.where(ds['t2m_avg'] > 40, 0, xr.where(ds['t2m_avg'] >= 35, 3, xr.where(ds['t2m_avg'] >= 30, 1+(39-ds['t2m_avg']), xr.where(ds['t2m_avg'] >= 10, 10+((30-ds['t2m_avg'])*0.5), xr.where(ds['t2m_avg'] >= 1, 20-((10-ds['t2m_avg'])*0.5), xr.where(ds['t2m_avg'] >= -4, 15-(0-ds['t2m_avg']), 10))))))

    ds['tp_maxed'] = ds['tp'].copy()
    ds['tp_maxed'] = xr.where((ds['tp_maxed']) > 0.5, 0.5,
                                      ds['tp_maxed'])

    ds['ptype'] = xr.where((ds['tp']) < 0.01, 0.25,
                    xr.where(ds['t2m_avg'] > 40., 0.5+(ds['tp_maxed']),
                             xr.where(ds['t2m_avg'] > 35.0, 1+(ds['tp_maxed']),
                                      1.5+(ds['tp_maxed']))))

    ds['slr'] = ds['slr'].where(ds['slr'] > 3.01).fillna(0)

    ds['snow'] = ds['tp'].copy()
    ds['snow'] = ds['snow']*ds['slr']

    #assign init coordinate with datestr, cycle
    ds = ds.assign_coords({'init':datestr+cycle})

    # if f == 3:
    #     total_ds = ds.copy()
    #     # total_ds = total_ds[['tp','snow']]
    #     total_ds['total_precip'] = total_ds['tp']
    #     total_ds['total_snow'] = total_ds['snow']
    #     total_ds.to_netcdf('/Users/clamalo/documents/ensemble-blend/total_gribs/gefs_'+name_frame(f)+'.nc')
    # else:
    #     old_total_ds = xr.open_dataset('/Users/clamalo/documents/ensemble-blend/total_gribs/gefs_'+name_frame(f-3)+'.nc')
    #     old_total_ds['total_precip'] = old_total_ds['total_precip'] + ds['tp']
    #     old_total_ds['total_snow'] = old_total_ds['total_snow'] + ds['snow']

    #     old_total_ds['tp'] = ds['tp']
    #     old_total_ds['snow'] = ds['snow']
        
    #     old_total_ds['t2m'] = ds['t2m']
    #     old_total_ds['slr'] = ds['slr']
    #     old_total_ds['ptype'] = ds['ptype']
    #     old_total_ds['t2m_avg'] = ds['t2m_avg']

    #     old_total_ds.to_netcdf('/Users/clamalo/documents/ensemble-blend/total_gribs/gefs_'+name_frame(f)+'.nc')

    #     total_ds = old_total_ds.copy()
    #     total_ds['t2m'] = ds['t2m']
    #     total_ds['slr'] = ds['slr']

    if f == 3:
        total_ds = ds.copy()
        total_ds = total_ds[['tp','snow']]
        total_ds.to_netcdf('/Users/clamalo/documents/ensemble-blend/total_gribs/gefs_'+name_frame(f)+'.nc')
    else:
        old_total_ds = xr.open_dataset('/Users/clamalo/documents/ensemble-blend/total_gribs/gefs_'+name_frame(f-3)+'.nc')
        old_total_ds['tp'] = old_total_ds['tp'] + ds['tp']
        old_total_ds['snow'] = old_total_ds['snow'] + ds['snow']
        old_total_ds.to_netcdf('/Users/clamalo/documents/ensemble-blend/total_gribs/gefs_'+name_frame(f)+'.nc')

        total_ds = old_total_ds.copy()
        total_ds['t2m'] = ds['t2m']
        total_ds['slr'] = ds['slr']

    points = plot_hourly_snow(ds,f,points,domains)
    points = plot_total_snow(total_ds,f,points,domains)
    points = plot_hourly_precip(ds,f,points,domains)
    points = plot_total_precip(total_ds,f,points,domains)
    points = plot_temperature(ds,f,points,domains)
    points = plot_slr(ds,f,method,points,domains)
    points = plot_ptype(ds,f,points,domains)

    if f != 168:
        continue

    for n in range(len(points)):

        point_name = points[n][0]
        point_lat = float(points[n][1])
        point_lon = float(points[n][2])

        point_elevation = int(float(elevation_ds.sel(lat=point_lat,lon=point_lon,method='nearest').elevation.values)*3.28084)

        timezone_str = tz.tzNameAt(point_lat, point_lon)
        to_zone = dateutil.gettz(timezone_str)

        tick_label_list = []
        for x in range(3,f+1,12):
            tick_datestr = str(datestr)+str(cycle)
            tick_datestr = datetime.strptime(tick_datestr, '%Y%m%d%H')
            hours_added = timedelta(hours = int(x))
            tick_datestr = tick_datestr+hours_added
            tick_datestr = tick_datestr.replace(tzinfo=from_zone)
            tick_datestr = str(tick_datestr.astimezone(to_zone))
            tick_datestr = tick_datestr.split('-')
            tick_datestr = (tick_datestr[0]+tick_datestr[1]+tick_datestr[2]).split(' ')
            tick_datestr = str(tick_datestr[0]+(tick_datestr[1]).split(':')[0])
            tick_datestr = tick_datestr[4:6]+'/'+tick_datestr[6:8]+' '+tick_datestr[8:10]
            tick_label_list.append(tick_datestr)

        plt.figure(figsize=(15,9))
        plt.subplot(3,2,1)
        plt.plot(points[n][5],color='blue',linewidth=2)
        plt.title('Snow')
        # plt.ylim(0,max(points[n][5])*1.05)
        max_tick = float(round(max(points[n][5]),1)+1)
        plt.ylim(0, max_tick)
        plt.xlim(0,int(f/3)-1)
        plt.grid()

        plt.subplot(3,2,2)
        plt.plot(points[n][6],color='blue',linewidth=2)
        plt.title('Total Snow')
        # plt.ylim(0,max(points[n][6])*1.05)
        max_tick = float(round(max(points[n][6]),1)+1)
        plt.ylim(0, max_tick)
        plt.xlim(0,int(f/3)-1)
        plt.grid()

        plt.subplot(3,2,3)
        plt.plot(points[n][7],color='green',linewidth=2)
        plt.title('Precip')
        # plt.ylim(0,max(points[n][7])*1.05)
        max_tick = float(round(max(points[n][7]),1)+0.1)
        plt.ylim(0, max_tick)
        plt.xlim(0,int(f/3)-1)
        plt.grid()

        plt.subplot(3,2,4)
        plt.plot(points[n][8],color='green',linewidth=2)
        plt.title('Total Precip')
        # plt.ylim(0,max(points[n][8])*1.05)
        max_tick = float(round(max(points[n][8]),1)+0.1)
        plt.ylim(0, max_tick)
        plt.xlim(0,int(f/3)-1)
        plt.grid()

        plt.subplot(3,2,5)
        plt.plot(points[n][9],color='red',linewidth=2)
        plt.title('Temperature')
        max_tick = float(round(max(points[n][9]),1)+5)
        min_tick = float(round(min(points[n][9]),1)-5)
        plt.ylim(min_tick,max_tick)
        plt.xlim(0,int(f/3)-1)
        plt.xticks(np.arange(0,int(f/3),4),tick_label_list)
        plt.xticks(rotation = 45)
        plt.xticks(fontsize=7)
        plt.grid()

        plt.subplot(3,2,6)
        plt.plot(points[n][10],color='black',linewidth=2)
        plt.title('SLR')
        # plt.ylim(0,max(points[n][10])*1.05)
        max_tick = float(round(max(points[n][10]),1)+2)
        plt.ylim(0, max_tick)
        plt.xlim(0,int(f/3)-1)
        plt.xticks(np.arange(0,int(f/3),4),tick_label_list)
        plt.xticks(rotation = 45)
        plt.xticks(fontsize=7)
        plt.grid()

        plt.setp(plt.gcf().get_axes()[:-2], xticks=range(0, int(f/3), 4), xticklabels=[])
        init_label = datestr[4:6]+'/'+datestr[6:8]+' '+cycle+'z'
        plt.suptitle("Point Forecast: "+point_name+" (Grid Elevation: "+str(point_elevation)+"') - Init: "+init_label, fontsize=16)

        plt.savefig('/Users/clamalo/documents/ensemble-blend/images/points/'+point_name+'_all.png',bbox_inches='tight',dpi=200)