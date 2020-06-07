import pandas as pd
import numpy as np
import time
import json
from flask import jsonify, abort
import flask

global_timeseries_path = \
    './COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

df = pd.read_csv(global_timeseries_path)
start_date = df.columns[4]
start_date = time.strftime('%Y-%m-%d', time.strptime(start_date, '%m/%d/%y'))
days = len(df.columns) - 4


def get_country_wise_data():
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

    country_case_sum = df.groupby(country)[cases].apply(np.sum)
    country_lat_mean = df.groupby(country)[lat].apply(np.mean)
    country_long_mean = df.groupby(country)[long].apply(np.mean)

    country_agg = pd.concat([country_lat_mean, country_long_mean, country_case_sum], axis=1)
    return country_agg


c_wise = get_country_wise_data()


if not __name__ == '__main__':
    from backend import app
    import error_handlers
    import exceptions


    @app.route('/country_stats/<country_name>')
    def get_country_stats(country_name):
        try:
            country_stats = c_wise.loc[country_name]
        except KeyError:
            abort(404)
        # todo: get rid of this hack job
        dct = country_stats.to_json()
        dct = json.loads(dct)
        dct['start_date'] = start_date
        dct['num_days'] = days
        return dct