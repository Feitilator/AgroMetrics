from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / 'cache'
DATA_DIR = ROOT / 'data'
MODEL_DIR = ROOT / 'models'

START_DATE = '2010-01-01'
END_DATE = '2025-12-31'
HORIZON_DAYS = 7
MIN_CLIMATOLOGY_YEARS = 5

REGIONS = [
    'Akmola Region', 'Aktobe Region', 'Almaty Region', 'Atyrau Region',
    'West Kazakhstan Region', 'Zhambyl Region', 'Zhetisu Region',
    'Karaganda Region', 'Kostanay Region', 'Kyzylorda Region',
    'Mangystau Region', 'Pavlodar Region', 'North Kazakhstan Region',
    'Turkistan Region', 'Abai Region', 'Ulytau Region', 'East Kazakhstan Region',
]

OPEN_METEO_ARCHIVE = 'https://archive-api.open-meteo.com/v1/archive'
OPEN_METEO_GEOCODING = 'https://geocoding-api.open-meteo.com/v1/search'
NASA_POWER_DAILY = 'https://power.larc.nasa.gov/api/temporal/daily/point'

WEATHER_DAILY = [
    'temperature_2m_mean', 'temperature_2m_max', 'temperature_2m_min',
    'precipitation_sum', 'rain_sum', 'snowfall_sum',
    'wind_speed_10m_max', 'wind_gusts_10m_max',
    'shortwave_radiation_sum', 'et0_fao_evapotranspiration',
    'vapour_pressure_deficit_mean',
    'soil_moisture_0_to_7cm_mean', 'soil_moisture_7_to_28cm_mean',
    'soil_moisture_28_to_100cm_mean', 'snow_depth_mean',
]

NASA_PARAMETERS = [
    'T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'RH2M', 'WS10M',
    'ALLSKY_SFC_SW_DWN', 'ALLSKY_SFC_LW_DWN', 'T2MDEW', 'PS'
]
