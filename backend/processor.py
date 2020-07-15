# -*- coding: utf-8 -*-

from scipy.spatial import distance
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta

dirpath = os.path.dirname(__file__)
dirpath = os.path.join(dirpath, 'dataset')

global_active_csv = os.path.join(dirpath,
                                 'time_series_covid19_confirmed_global.csv')
global_death_csv = os.path.join(dirpath,
                                'time_series_covid19_deaths_global.csv')
global_recover_csv = os.path.join(dirpath,
                                  'time_series_covid19_recovered_global.csv')
us_active_csv = os.path.join(dirpath,
                             'time_series_covid19_confirmed_US.csv')
us_death_csv = os.path.join(dirpath,
                            'time_series_covid19_deaths_US.csv')


# us_recover_csv = \
#     './dataset/time_series_covid19_recovered_global.csv'


def load_data(csv_time_series_file_path, date_column_index=4):
    df = pd.read_csv(csv_time_series_file_path)

    date_list = list(df.columns[date_column_index:])
    date_list = [*map(lambda x: time.strptime(x, '%m/%d/%y'), date_list)]

    start_date = date_list[0]
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
    # has_regions = df[state].notnull()
    country_has_regions = df.groupby(country)[state].any()
    country_has_regions.rename('has_regions', inplace=True)

    country_regions = df.groupby(country)[state].apply(list)
    country_regions.rename('regions', inplace=True)

    country_agg = pd.concat(
        [country_lat_mean, country_long_mean, country_case_sum, country_has_regions, country_regions], axis=1)

    region_df = df[df[state].notnull()]

    return country_agg, region_df


def preprocess_us(df, date_column_index):
    state = df.columns[6]
    county = df.columns[5]
    lat = df.columns[8]
    long = df.columns[9]
    cases = 'cases'

    dates = df.columns[date_column_index:]

    ts_list = list(df[dates].values)
    df.drop(columns=dates, inplace=True)
    df[cases] = ts_list

    df.rename(columns={long: 'Long', state: 'Province/State', county: 'County'}, inplace=True)
    state = 'Province/State'
    county = 'County'
    long = 'Long'

    state_case_sum = df.groupby(state)[cases].apply(np.sum)
    state_lat_mean = df.groupby(state)[lat].apply(np.mean)
    state_long_mean = df.groupby(state)[long].apply(np.mean)
    state_long_mean.rename('Long', inplace=True)

    state_has_regions = df.groupby(state)[county].any()
    state_has_regions.rename('has_subregions', inplace=True)

    state_regions = df.groupby(state)[county].apply(list)
    state_regions.rename('subregions', inplace=True)

    state_agg = pd.concat(
        [state_lat_mean, state_long_mean, state_case_sum, state_has_regions, state_regions], axis=1)
    state_agg.insert(loc=0, column='Country/Region', value='US')
    state_agg.reset_index(inplace=True)

    return state_agg, df


def combine_global_and_us(country_agg, region_agg, us_state_agg):
    country_agg.loc['US', 'has_regions'] = True
    country_agg.at['US', 'regions'] = list(us_state_agg['Province/State'])

    # bring US regions and global regions in the same table
    region_agg['has_subregions'] = False
    region_agg['subregions'] = None

    region_agg = pd.concat((region_agg, us_state_agg))
    region_agg.reset_index(drop=True, inplace=True)

    return country_agg, region_agg


df_cases, date_list, start_date, days = load_data(global_active_csv)
df_recov, date_list_recov, start_date_recov, days_recov = load_data(global_recover_csv)
df_death, date_list_death, start_date_death, days_death = load_data(global_death_csv)

us_cases, us_date_list, us_start_date, us_days = load_data(us_active_csv, date_column_index=11)
us_death, us_date_list_death, us_start_date_death, us_days_death = load_data(us_death_csv, date_column_index=12)


c_wise, r_wise = get_country_wise_data(df_cases)
us_state_wise, us_county_wise = preprocess_us(us_cases, date_column_index=11)
c_wise, r_wise = combine_global_and_us(c_wise, r_wise, us_state_wise)

c_wise_arr = np.vstack(c_wise['cases'].values)
c_names = list(c_wise.index)

r_names = c_wise['regions'].values
r_dict = dict(zip(c_names, r_names))

c_num_countries = c_wise_arr.shape[0]
c_num_days = c_wise_arr.shape[1]


# ASSUMPTION - holds so far - all different files have same number of countries
c_wise_recov, r_wise_recov = get_country_wise_data(df_recov)
c_wise_recov_arr = np.vstack(c_wise_recov['cases'].values)

c_wise_death, r_wise_death = get_country_wise_data(df_death)
us_state_wise_death, us_county_wise_death = preprocess_us(us_death, date_column_index=12)
c_wise_death, r_wise_death = combine_global_and_us(c_wise_death, r_wise_death, us_state_wise_death)

c_wise_death_arr = np.vstack(c_wise_death['cases'].values)

if not __name__ == '__main__':
    from backend import app
    from . import error_handlers
    from . import exceptions
    from flask import jsonify, abort, request


    @app.route('/list/countries')
    @app.route('/country_stats/list_all_countries')
    def list_all_countries():
        return jsonify(c_names)


    @app.route('/list/regions')
    def list_all_regions():
        return r_dict


    @app.route('/locate/<country_name>/')
    def locate_country(country_name):
        try:
            loc = c_wise.loc[country_name, ['Lat', 'Long']]
        except KeyError:
            abort(404, error_handlers.invalid_country_msg)
        return loc.to_dict()


    @app.route('/locate/<country_name>/<region_name>/')
    def locate_region(country_name, region_name):
        # todo: repeated fragment here and in stats
        region = r_wise.columns[0]
        country = r_wise.columns[1]
        # r_wise and c_wise are global.
        country_mask = r_wise[country] == country_name
        # todo: improve approach. pd.DataFrame/Series.any also works
        if not np.any(country_mask):
            # country name invalid or country doesn't have regions
            abort(404, error_handlers.invalid_country_or_no_regions_msg)
        region_mask = r_wise[region] == region_name
        combined_mask = region_mask & country_mask
        if not np.any(combined_mask):
            # region incorrect
            abort(404, error_handlers.invalid_region_msg)

        loc = r_wise[combined_mask].iloc[0][['Lat', 'Long']].to_dict()
        return loc


    @app.route('/stats/<country_name>/')
    @app.route('/country_stats/<country_name>/')
    def get_country_stats(country_name):
        # c_wise is global
        try:
            country_stats = c_wise.loc[country_name]
            country_stats_recov = c_wise_recov.loc[country_name]
            country_stats_death = c_wise_death.loc[country_name]
        except KeyError:
            abort(404, error_handlers.invalid_country_msg)
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


    @app.route('/stats/<country_name>/<region_name>/')
    @app.route('/country_stats/<country_name>/<region_name>/')
    def get_region_stats(country_name, region_name):
        region = r_wise.columns[0]
        country = r_wise.columns[1]
        # r_wise and c_wise are global.
        country_mask = r_wise[country] == country_name
        # todo: improve approach. pd.DataFrame/Series.any also works
        if not np.any(country_mask):
            # country name invalid or country doesn't have regions
            abort(404, error_handlers.invalid_country_or_no_regions_msg)
        region_mask = r_wise[region] == region_name
        combined_mask = region_mask & country_mask
        if not np.any(combined_mask):
            # region incorrect
            abort(404, error_handlers.invalid_region_msg)

        dct = r_wise[combined_mask].iloc[0]  # mask gives a container of rows, we need the first row
        dct_death = r_wise_death[combined_mask].iloc[0]

        # to json and back hack job
        # todo: define json-izing of np arrays
        dct = dct.to_json()
        dct_death = dct_death.to_json()

        dct = json.loads(dct)
        dct_death = json.loads(dct_death)

        # end hack job

        dct['start_date'] = start_date
        dct['num_days'] = days
        dct['deaths'] = dct_death['cases']

        # todo: regional recovery data unavailable for US
        if country_name != 'US':
            dct_recov = r_wise[combined_mask].iloc[0]
            dct_recov = dct_recov.to_json()
            dct_recov = json.loads(dct_recov)
            dct['recovered'] = dct_recov['cases']
        else:
            dct['recovered'] = None
        del dct[country]
        del dct[region]

        # todo: don't delete. give country name and region name
        return dct


    @app.route('/compare/<country_name>')
    @app.route('/compare_countries/<country_name>')
    def get_similar_from_countries(country_name):
        try:
            window = request.args.get('window', type=int)
        except ValueError:
            abort(400, error_handlers.invalid_window_msg)
        if window is None or window < 1 or window > days:
            abort(400, error_handlers.invalid_window_msg)

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
            abort(400, error_handlers.invalid_type_msg)

        date = request.args.get('date')
        if date is None:
            date = dates[-1]
            col_index = c_num_days - 1
        else:
            try:
                date = time.strptime(date, '%Y-%m-%d')
            except ValueError:
                # date format is invalid
                abort(400, error_handlers.invalid_date_fmt)
            try:
                col_index = dates.index(date)
            except ValueError:
                # date is out of range
                abort(404, error_handlers.date_out_of_range)

        try:
            country_history = df['cases'][country_name]
        except KeyError:
            # country_name invalid
            abort(400, error_handlers.invalid_country_msg)

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
