import pandas as pd
import numpy as np

global_timeseries_path = \
    './COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

df = pd.read_csv(global_timeseries_path)

state = df.columns[0]
country = df.columns[1]
lat = df.columns[2]
long = df.columns[3]
cases = 'cases'
# combine date columns
dates = df.columns[4:]
ts_list = list(df[dates].values)
df.drop(columns=dates, inplace=True)
df[cases] = ts_list

country_agg = df.groupby(country)[cases].apply(np.sum)

