# -*- coding: utf-8 -*-

from scipy.spatial import distance
import pandas as pd
import numpy as np
import time
import json
from datetime import datetime, timedelta

global_active_csv = \
    './COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
global_death_csv = \
    './COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
global_recover_csv = \
    './COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'


def load_data(csv_time_series_file_path):
    df = pd.read_csv(csv_time_series_file_path)

    date_list = list(df.columns[4:])
    date_list = [*map(lambda x: time.strptime(x, '%m/%d/%y'), date_list)]

    # start_date = df.columns[4]
    start_date = date_list[0]
    # start_date_t = time.strptime(start_date, '%m/%d/%y')
    start_date = time.strftime('%Y-%m-%d', start_date)

    days = len(df.columns) - 4
    return df, date_list, start_date, days


def get_country_wise_data(df):
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


df_cases, date_list, start_date, days = load_data(global_active_csv)
df_recov, date_list_recov, start_date_recov, days_recov = load_data(global_recover_csv)
df_death, date_list_death, start_date_death, days_death = load_data(global_death_csv)

c_wise = get_country_wise_data(df_cases)
c_wise_arr = np.vstack(c_wise['cases'].values)
c_names = list(c_wise.index)
c_num_countries = c_wise_arr.shape[0]
c_num_days = c_wise_arr.shape[1]

# ASSUMPTION - holds so far - all different files have same number of countries
c_wise_recov = get_country_wise_data(df_recov)
c_wise_recov_arr = np.vstack(c_wise_recov['cases'].values)

c_wise_death = get_country_wise_data(df_death)
c_wise_death_arr = np.vstack(c_wise_death['cases'].values)


if not __name__ == '__main__':
    from backend import app
    from . import error_handlers
    from . import exceptions
    from flask import jsonify, abort, request


    @app.route('/country_stats/list_all_countries')
    def list_all_countries():
        return jsonify(c_names)

    @app.route('/locate/<country_name>')
    def locate_country(country_name):
        try:
            loc = c_wise.loc[country_name, ['Lat', 'Long']]
        except KeyError:
            abort(404)
        return loc.to_dict()

    @app.route('/country_stats/<country_name>')
    def get_country_stats(country_name):
        # c_wise is global
        try:
            country_stats = c_wise.loc[country_name]
            country_stats_recov = c_wise_recov.loc[country_name]
            country_stats_death = c_wise_death.loc[country_name]
        except KeyError:
            abort(404)
        # todo: get rid of this hack job
        dct = country_stats.to_json()
        dct_recov = country_stats_recov.to_json()
        dct_death = country_stats_death.to_json()

        dct = json.loads(dct)
        dct_recov = json.loads(dct_recov)
        dct_death = json.loads(dct_death)

        dct['start_date'] = start_date
        dct['num_days'] = days
        dct['deaths'] = dct_death['cases']
        dct['recovered'] = dct_recov['cases']
        return dct

    @app.route('/compare_countries/<coutry_name>')
    def get_similar_from_countries(coutry_name):
        try:
            window = request.args.get('window', type=int)
        except ValueError:
            abort(400)
        if window is None or window < 1 or window > days:
            abort(400)

        data_type = request.args.get('type', default='cases')

        if data_type == 'cases':
            df = c_wise
            cases_arr = c_wise_arr
            dates = date_list
        elif data_type == 'deaths':
            df = c_wise_death
            cases_arr = c_wise_death_arr
            dates = date_list_death
        elif data_type == 'recovered':
            df = c_wise_recov
            cases_arr = c_wise_recov_arr
            dates = date_list_recov
        else:
            # type not understaood
            abort(400)

        date = request.args.get('date')
        if date is None:
            date = dates[-1]
            col_index = c_num_days - 1
        else:
            try:
                date = time.strptime(date, '%Y-%m-%d')
            except ValueError:
                # date format is invalid
                abort(400)
            try:
                col_index = dates.index(date)
            except ValueError:
                # date is out of range
                abort(404)

        try:
            country_history = df['cases'][coutry_name]
        except KeyError:
            # country_name invalid
            abort(400)

        slice_right = col_index + 1
        slice_left = col_index - window + 1
        # todo: add padding? currently the window is reduced.
        slice_left = 0 if slice_left < 0 else slice_left

        test_sample = country_history[slice_left:slice_right]

        # todo: memoize for different windows? Don't recalculate
        dist_arr = np.zeros(cases_arr.shape, dtype=np.float)
        dist_arr[:, 0:window - 1] = np.inf

        for i in range(cases_arr.shape[0]):
            for j in range(window - 1, cases_arr.shape[1]):
                dist = distance.euclidean(cases_arr[i, j - window + 1:j + 1], test_sample)
                dist_arr[i, j] = dist

        arg_mins = np.argmin(dist_arr, axis=1)
        mins = np.min(dist_arr, axis=1)
        c_inds = np.arange(len(mins))

        arg_sort = np.argsort(mins)

        result = []
        # skip the first, that is query point itself
        for i in range(1, len(arg_sort)):
            ind = arg_sort[i]
            result.append(
                {
                    "rank": i,
                    "country": c_names[c_inds[ind]],
                    "date": time.strftime('%Y-%m-%d', dates[arg_mins[ind]]),
                    "distance": mins[ind]
                }
            )
        return jsonify(result)
