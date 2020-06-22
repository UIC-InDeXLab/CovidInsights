# [!] FUTURE DEPRECATE.
# Marked for deprecation. This file doesn't use pandas. to be removed later on.
#

import time
import numpy as np
import csv
from scipy import signal
from scipy import stats
from scipy.spatial import distance
from matplotlib import pyplot as plt
from . import exceptions

global_timeseries_path = './COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

# CSV Columns are as follows:
# Province / State, Country / Region, Lat, Long, date1, date2, ... , daten
# 0: province
# 1: country
# 2: lat
# 3: long
# 4:end dates

data = []
data_arr = []
loc_arr = []
region_list = []
country_list = []
country_dict = {}

with open(global_timeseries_path, 'rt') as file:
    header = file.readline()
    header = header.rstrip().split(',')
    dates = header[4:]

    # machine readable dates
    dates_mr = [*map(lambda x: time.strptime(x, '%m/%d/%y'), dates)]

    csv_reader = csv.reader(file)
    for line in csv_reader:
        data.append(line)

        region_name = line[0]
        country_name = line[1]
        lat = line[2]
        long = line[3]
        region_list.append(region_name)
        country_list.append(country_name)

        loc_row = [*map(float, line[2:4])]
        loc_arr.append(loc_row)

        # todo: improve country_dict. add_regions
        country_dict[line[1]] = {'lat': loc_row[0],
                                 'long': loc_row[1],
                                 'regions': None}

        data_row = np.array([*map(int, line[4:])])
        data_arr.append(data_row)

data_arr = np.array(data_arr)
loc_arr = np.array(loc_arr)

date_to_index = dict(zip(dates_mr, range(len(dates_mr))))

# If country given, takes the entire country, otherwise region

given_country = 'Afghanistan'
given_date = '4/9/20'
window = 7

try:
    date_mr = time.strptime(given_date, '%m/%d/%y')
except ValueError:
    print("Invalid date")
    # todo: return here

# todo: cater for regions
try:
    row_index = country_list.index(given_country)
except ValueError:
    print("Invalid country")


col_index = date_to_index[date_mr]
# pad_left here
test_sample = data_arr[row_index, col_index-window+1:col_index+1]
print(test_sample)

dist_arr = np.zeros(data_arr.shape, dtype=np.float)
dist_arr[:, 0:window-1] = np.inf

for i in range(len(data_arr)):
    for j in range(window-1, len(data_row)):
        dist = distance.euclidean(data_arr[i, j-window+1:j+1], test_sample)
        dist_arr[i, j] = dist


def get_country_data(country):
    try:
        row_index = country_list.index(country)
    except ValueError:
        raise exceptions.InvalidCountryException

    start_date = time.strftime('%Y-%m-%d', dates_mr[0])
    end_date = time.strftime('%Y-%m-%d', dates_mr[-1])
    data = data_arr[row_index, :]
    # todo: fix this hack job
    # need to convert to python ints (instead of np.int) for jsonify to work
    data = list(map(int, data))
    return data, start_date, end_date