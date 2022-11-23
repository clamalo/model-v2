import xarray as xr
from osgeo import gdal
import requests
import numpy as np

def name_frame(n):
    if int(n) < 10:
        return "00" + str(n)
    elif int(n) < 100:
        return "0" + str(n)
    else:
        return str(n)

def find_temperature(gh1,gh2,elevation):
    temperature = gh1['t'] + (gh2['t'] - gh1['t']) * ((elevation - gh1['gh']) / (gh2['gh'] - gh1['gh']))
    return temperature

elevation_ds = xr.load_dataset('/Users/clamalo/documents/elevation.nc')
elevation_ds = elevation_ds.sel(lat=slice(37,41), lon=slice(-109,-104))


for f in range(0,145,3):
    datestr,cycle = '20221122','06'
    # url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t12z.pgrb2.0p25.f'+name_frame(f)+'&lev_1000_mb=on&lev_600_mb=on&lev_700_mb=on&lev_800_mb=on&lev_900_mb=on&var_HGT=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.20221121%2F12%2Fatmos'
    # url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?file=geavg.t12z.pgrb2a.0p50.f'+name_frame(f)+'&lev_1000_mb=on&lev_500_mb=on&lev_700_mb=on&lev_850_mb=on&lev_925_mb=on&var_HGT=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.20221121%2F12%2Fatmos%2Fpgrb2ap5'
    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?file=geavg.t'+cycle+'z.pgrb2a.0p50.f'+name_frame(f)+'&lev_1000_mb=on&lev_2_m_above_ground=on&lev_500_mb=on&lev_700_mb=on&lev_850_mb=on&lev_925_mb=on&lev_surface=on&var_HGT=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.'+datestr+'%2F'+cycle+'%2Fatmos%2Fpgrb2ap5'
    print(url)
    response = requests.get(url)
    with open('/Users/clamalo/downloads/'+name_frame(f)+'.grib2', 'wb') as file:
        file.write(response.content)

    continue

    ds = xr.load_dataset('/Users/clamalo/downloads/'+name_frame(f)+'.grib2', engine="cfgrib")
    #convert (0,360) to (-180,180)
    ds['longitude'] = (ds['longitude'] + 180) % 360 - 180

    #interpolate ds to elevation_ds
    ds = ds.interp(latitude=elevation_ds.lat, longitude=elevation_ds.lon)#, method="zero")
    ds['elevation'] = elevation_ds['elevation']
    ds['elevation'] = ds['elevation'].fillna(0)


    gh1 = ds.isel(isobaricInhPa=0)
    gh2 = ds.isel(isobaricInhPa=1)
    gh3 = ds.isel(isobaricInhPa=2)
    gh4 = ds.isel(isobaricInhPa=3)
    gh5 = ds.isel(isobaricInhPa=4)

    if f == 0:
        orog_ds = ds.copy()

    ds['t2m'] = xr.where(ds['elevation'] < gh2['gh'], find_temperature(gh1,gh2,ds['elevation']), xr.where(ds['elevation'] < gh3['gh'], find_temperature(gh2,gh3,ds['elevation']), xr.where(ds['elevation'] < gh4['gh'], find_temperature(gh3,gh4,ds['elevation']),find_temperature(gh4,gh5,ds['elevation']))))



    # ds['isobaric_above_orog'] = xr.where(orog_ds['orog'] < gh1['gh'], 0, xr.where(orog_ds['orog'] < gh2['gh'], 1, xr.where(orog_ds['orog'] < gh3['gh'], 2, xr.where(orog_ds['orog'] < gh4['gh'], 3, 4))))
    # # #same as above line but make sure the gh is at least 500m above the orog
    # # ds['isobaric_above_orog'] = xr.where(orog_ds['orog'] < gh1['gh'] + 500, 0, xr.where(orog_ds['orog'] < gh2['gh'] + 500, 1, xr.where(orog_ds['orog'] < gh3['gh'] + 500, 2, xr.where(orog_ds['orog'] < gh4['gh'] + 500, 3, 4))))

    # ds['lapse_rate'] = xr.where(ds['isobaric_above_orog'] == 0, (gh2['t'] - gh1['t']) / (gh2['gh'] - gh1['gh']), xr.where(ds['isobaric_above_orog'] == 1, (gh3['t'] - gh2['t']) / (gh3['gh'] - gh2['gh']), xr.where(ds['isobaric_above_orog'] == 2, (gh4['t'] - gh3['t']) / (gh4['gh'] - gh3['gh']), (gh5['t'] - gh4['t']) / (gh5['gh'] - gh4['gh']))))

    # # ds['t2m'] = xr.where(ds['elevation'] < orog_ds['orog'], (ds.isel(isobaricInhPa=ds['isobaric_above_orog'])['t']+(ds.isel(isobaricInhPa=ds['isobaric_above_orog'])['t']-ds.isel(isobaricInhPa=ds['isobaric_above_orog']-1)['t'])/(ds.isel(isobaricInhPa=ds['isobaric_above_orog']-1)['gh']-ds.isel(isobaricInhPa=ds['isobaric_above_orog'])['t'])*(ds.isel(isobaricInhPa=ds['isobaric_above_orog']-1)['t']-ds['elevation'])), ds['t2m'])
    # ds['t2m'] = xr.where(ds['elevation'] < orog_ds['orog'], ds['t2m']+ds['lapse_rate']*(ds['elevation']-orog_ds['orog']),xr.where(ds['elevation'] < gh2['gh'], find_temperature(gh1,gh2,ds['elevation']), xr.where(ds['elevation'] < gh3['gh'], find_temperature(gh2,gh3,ds['elevation']), xr.where(ds['elevation'] < gh4['gh'], find_temperature(gh3,gh4,ds['elevation']),find_temperature(gh4,gh5,ds['elevation'])))))

    # # (ds.isel(isobaricInhPa=ds['isobaric_above_orog'])['t']+(ds.isel(isobaricInhPa=ds['isobaric_above_orog'])['t']-ds.isel(isobaricInhPa=ds['isobaric_above_orog']-1)['t'])/(ds.isel(isobaricInhPa=ds['isobaric_above_orog']-1)['gh']-ds.isel(isobaricInhPa=ds['isobaric_above_orog'])['t'])*(ds.isel(isobaricInhPa=ds['isobaric_above_orog']-1)['t']-ds['elevation']))


    lat,lon = 39.13106, -106.86084
    value = (ds['t2m'].sel(lat=lat, lon=lon, method='nearest').values)

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    # ax.set_extent([-125, -120, 45, 52], crs=ccrs.PlateCarree())
    ax.coastlines(resolution='50m', color='black', linewidth=1)
    ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')

    cf = ax.pcolormesh(ds['longitude'], ds['latitude'], ds['t2m'], transform=ccrs.PlateCarree(), cmap='jet',vmin=260,vmax=290)
    plt.colorbar(cf, ax=ax, shrink=0.5)
    plt.savefig(str(f)+'test.png', dpi=300)