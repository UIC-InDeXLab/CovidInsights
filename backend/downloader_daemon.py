import os
import requests
import time
import pickle

updates_made = False

dirpath = os.path.dirname(__file__)
dirpath = os.path.join(dirpath, 'dataset')
script = os.path.basename(__file__)
script_sleep_time = 3600

git_commit_history_url = 'https://api.github.com/repos/CSSEGISandData/COVID-19/commits'

# tuples of (local name, remote link)
file_set = [
    ('time_series_covid19_confirmed_global.csv', 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                                                 '/csse_covid_19_data/csse_covid_19_time_series'
                                                 '/time_series_covid19_confirmed_global.csv'),
    ('time_series_covid19_confirmed_US.csv', 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                                             '/csse_covid_19_data/csse_covid_19_time_series'
                                             '/time_series_covid19_confirmed_US.csv'),
    ('time_series_covid19_deaths_global.csv', 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                                              '/csse_covid_19_data/csse_covid_19_time_series'
                                              '/time_series_covid19_deaths_global.csv'),
    ('time_series_covid19_deaths_US.csv', 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                                          '/csse_covid_19_data/csse_covid_19_time_series'
                                          '/time_series_covid19_deaths_US.csv'),
    ('time_series_covid19_recovered_global.csv', 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                                                 '/csse_covid_19_data/csse_covid_19_time_series'
                                                 '/time_series_covid19_recovered_global.csv'),
]

header_time_fmt = '%a, %d %b %Y %H:%M:%S GMT'
arg_time_fmt = '%Y-%m-%dT%H:%M:%SZ'
timestamp_file = os.path.join(dirpath, 'timestamp.pickle')

try:
    with open(timestamp_file, 'rb') as tf:
        timestamp_dict = pickle.load(tf)
except:
    timestamp_dict = {}

# time.strftime(time_format, time.gmtime(ts))
for fname, url in file_set:
    fpath = os.path.join(dirpath, fname)
    if not os.path.exists(fpath) or timestamp_dict.get(fname) is None:
        request_time = time.time()
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f'{script}: received status {resp.status_code} when trying to access {url}'
                  f'\n{script}: {fname} download Failed.')
            continue

        else:
            with open(fpath, 'wt') as file:
                file.write(resp.text)
            updates_made = True
            timestamp_dict[fname] = request_time
            print(f'{script}: downloaded {fname} at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(request_time))}')
    else:
        # can't use file modified stamp because we are using commit times. Commit can be of \
        # different files
        last_update_time = timestamp_dict[fname]
        last_update_time = time.gmtime(last_update_time)
        header_time = time.strftime(header_time_fmt, last_update_time)
        arg_time = time.strftime(arg_time_fmt, last_update_time)

        # query github for newer commits
        # todo: enter checks if connection fails
        request_time = time.time()
        github_resp = requests.get(git_commit_history_url,
                                   # params={'since': arg_time}, Add since and it doesn't answer in 304.
                                   headers={'If-Modified-Since': header_time})
        # print(f'{script}: received status {resp.status_code} when trying to access {url}')
        if github_resp.status_code == 304:
            timestamp_dict[fname] = request_time
            print(f'{script}: {fname} up to date.')
        elif github_resp.status_code == 200:
            # now get the original files
            # the raw file url doesn't respond to If-Modified-Since
            request_time = time.time()
            resp = requests.get(url)
            if resp.status_code == 200:
                with open(fpath, 'wt') as file:
                    file.write(resp.text)
                updates_made = True
                timestamp_dict[fname] = request_time
                print(f'{script}: updated {fname} '
                      f'at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(request_time))}')
            else:
                print(f'{script}: failed to update {fname}')
        else:
            print(f'{script}: failed to query github for new commits.')

with open(timestamp_file, 'wb') as ts:
    pickle.dump(timestamp_dict, ts)
