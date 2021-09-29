import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess
import os

os.chdir('/Users/hausfath/Desktop/Climate Science/Carbon Brief/Warming Map/')

def calculate_scalars():
    '''
    Import annual assessed warming values for each scenario, and CMIP6 multimodel means.
    Calculate the ratio of AR6 assessed warming to CMIP6 warming for each SSP.
    '''
    assessed_ssp119 = pd.read_csv('tas_global_SSP1_1_9.csv')
    assessed_ssp126 = pd.read_csv('tas_global_SSP1_2_6.csv')
    assessed_ssp245 = pd.read_csv('tas_global_SSP2_4_5.csv')
    assessed_ssp370 = pd.read_csv('tas_global_SSP3_7_0.csv')
    assessed_ssp585 = pd.read_csv('tas_global_SSP5_8_5.csv')
    
    cmip6_mmm_ssp126 = pd.read_csv(
        'icmip6_tas_mon_onemean_ssp126_0-360E_-90-90N_n_mean1_anom_a.txt'
        , delimiter=r"\s+", skiprows=60, names=['Year', 'cmip6']
    )
    cmip6_mmm_ssp245 = pd.read_csv(
        'icmip6_tas_mon_onemean_ssp245_0-360E_-90-90N_n_mean1_anom_a.txt'
        , delimiter=r"\s+", skiprows=60, names=['Year', 'cmip6']
    )
    cmip6_mmm_ssp370 = pd.read_csv(
        'icmip6_tas_mon_onemean_ssp370_0-360E_-90-90N_n_mean1_anom_a.txt'
        , delimiter=r"\s+", skiprows=60, names=['Year', 'cmip6']
    )
    cmip6_mmm_ssp585 = pd.read_csv(
        'icmip6_tas_mon_onemean_ssp585_0-360E_-90-90N_n_mean1_anom_a.txt'
        , delimiter=r"\s+", skiprows=60, names=['Year', 'cmip6']
    )
    
    scalar_26 = pd.merge(assessed_ssp126, cmip6_mmm_ssp126, how='outer', on=['Year'])
    scalar_45 = pd.merge(assessed_ssp245, cmip6_mmm_ssp245, how='outer', on=['Year'])
    scalar_70 = pd.merge(assessed_ssp370, cmip6_mmm_ssp370, how='outer', on=['Year'])
    scalar_85 = pd.merge(assessed_ssp585, cmip6_mmm_ssp585, how='outer', on=['Year'])
    
    scalar_26 = combine_assessed_cmip(scalar_26)
    scalar_45 = combine_assessed_cmip(scalar_45)
    scalar_70 = combine_assessed_cmip(scalar_70)
    scalar_85 = combine_assessed_cmip(scalar_85)

    return {
        'scalar_ssp126' : scalar_26,
        'scalar_ssp245' : scalar_45,
        'scalar_ssp370' : scalar_70,
        'scalar_ssp585' : scalar_85    
    }


def combine_assessed_cmip(scalar):
    '''
    Convert CMIP6 multimodel mean timeseries into anomalies relative to 1850-1899. Use a LOESS smoother
    to remove short-term variability in the CMIP5 MMM series. Normalize AR6 assessed and smooted CMIP6 GSAT 
    to 2015 when AR6 assessed warming projections begin. Calculate a scalar based on the ratio of the two.
    '''
    scalar.sort_values(by=['Year'], inplace=True)
    scalar.reset_index(inplace=True)
    baseline_old = scalar.loc[(scalar['Year'] >= 1850) & (scalar['Year'] <= 1899)]
    scalar['cmip6'] = scalar['cmip6'] - baseline_old.mean()['cmip6']
    scalar['cmip6'] = lowess(scalar['cmip6'], scalar['Year'], is_sorted=True, frac=0.1)[:,1]

    baseline_new = scalar.loc[(scalar['Year'] == 2015)]
    scalar['Mean'] = scalar['Mean'] - baseline_new.mean()['Mean'] + baseline_new.mean()['cmip6']
    scalar['scalar'] = scalar['Mean'] / scalar['cmip6']
    scalar['scalar'][250] = scalar['scalar'][249] #no 2100 assessed warming value, replace with 2099 scalar
    scalar['scalar'].fillna(1, inplace=True) #Scalar of 1 for historical runs
    return scalar[['Year', 'Mean', 'cmip6', 'scalar']]


scalars = calculate_scalars()
df = pd.DataFrame()
df['year'] = scalars['scalar_ssp126']['Year']
for ssp in ['126', '245', '370', '585']:
    df['scaler_ssp_'+ssp] = scalars['scalar_ssp'+ssp]['scalar']

df[df['year'] >= 2015].to_csv('scalars.csv')