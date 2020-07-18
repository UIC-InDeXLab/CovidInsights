# COVID Analysis Backend


## Setup
###Python Libraries
Backend needs the following python packages:
- numpy
- pandas
- flask

A flask can be run on any WSGI server that supports flask.
This document uses gunicorn. 
`pip install gunicorn`

Pull this repo: `git clone https://github.com/asudeh/covid19`

### Run

First run downloader_daemon.py so that it can download the dataset.
Use Ctrl-C to kill the process after it says 'Signalling Update'.
If you need to run in on auto-update then use something like:
`nohup python downloader_daemon.py &`.
This will cause the daemon to run in background and check for updates every 4 hours.
To kill, however you'll need to do `kill [PID]`.

Run the server using flask:
```
$ cd covid19
$ export FLASK_APP=[/path/to/covid19]/backend/__init__.py
$ export FLASK_DEBUG=TRUE
$ flask run
```

Run using gunicorn on top of flask on a public IP:
```
$ gunicorn --bind [IP_address]:[port_number] --reload --reload-extra-file [/path/to/]covid19/backend/dataset/update.txt backend:app
```

Run using gunicorn as a daemon:
```
$ gunicorn --bind [IP_address]:[port_number] --daemon --reload --reload-extra-file [/path/to/]covid19/backend/dataset/update.txt backend:app
```

The path in --reload-extra needs to be absolute.

## API Spec
- `/country_stats/[country_name]` or `/stats/[country_name]`
    gives the cases in a country, with it's latitude and longitude
    
    detailed example response:
```
    {
    "Lat": 23.56,
    "Long": -45.23,
    "cases": [0, 0, 2, 4, ..., 100, 105, 109],   # an array of confirmed cases
    "deaths": [0, 0, 0, 0, ..., 10, 10, 11],     # array recording the number of deaths
    "recovered": [0, 0, 0, 0, ..., 36, 37, 39],  # array recording recoveries
    "num_days": 123,                             # the number of days in data = size of arrays
    "start_date": "2020-01-23",                  # the date the data starts from
    "has_regions": True,                         # True/False. True if you can further query a country's regions 
    "regions": ["Alabama", ..., "Wyoming"]       # names of regions in a country    
}
```
- `/stats/<country_name>/<region_name>` similar to above, but queries a region
- `/list/countries` lists all countries
- `/list/regions` list all regions
- `/locate/<country_name>` gives lat and long of the given country
- `/locate/<country_name>/<region_name>`
- `/compare_countries/<coutry_name>` or `/compare/<country_name>` gives other areas (countries or regions) that are similar
to the given country by taking a sample of size = window ending in date specifified in the date parameter.
 Need to pass the following GET parameters:
    - `date=YYYY-MM-DD` optional. If not given, takes the 
    latest available date in data
    - `window=<window_size:int>` 
    - `type=[cases|recovered|deaths]` optional choose which type of data to compare

Example: `/compare/Pakistan?date=2020-04-22&window=7&type=deaths`
- `/compare/[country_name]/[region_name]` same as above, except the query point is from a region
