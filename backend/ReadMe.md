# COVID Analysis Backend

This folder must have a copy of the JHU dataset.

So far the approach is pulling the repository everyday.

There might be better ways to do this.

## Setup

``> git clone https://github.com/CSSEGISandData/COVID-19.git``

## Update

```
> cd COVID-19
> git pull
```

## API Spec
- `/country_stats/[country_name]`
    gives the confirmed cases in a country, with it's latitude and longitude
    
    detailed example response:
```
    {
    "Lat": 23.56,
    "Long": -45.23,
    "cases": [0, 0, 2, 4, ..., 100, 105, 109],   # an array of confirmed cases
    "deaths": [0, 0, 0, 0, ..., 10, 10, 11],     # array recording the number of deaths
    "recovered": [0, 0, 0, 0, ..., 36, 37, 39],  # array recording recoveries
    "num_days": 123,                             # the number of days in data = size of arrays
    "start_date": 2020-01-23,                    # the date the data starts from
    "has_regions": True                          # True/False. True if you can further query a country's regions 
    }
```
- `/country_stats/list_all_countries` lists all countries
- `/locate/<country_name>` gives lat and long of the given country
- `/compare_countries/<coutry_name>` gives other countries that are similar
to the given country by taking a sample of size = window ending in date specifified in the date parameter.
 Need to pass the following GET parameters:
    - `date=YYYY-MM-DD` optional. If not given, takes the 
    latest available date in data
    - `window=<window_size:int>` 
    - `type=[cases|recovered|deaths]` choose which type of data to compare

Example: `/compare_countries/Pakistan?date=2020-04-22&window=7&type=deaths`
    
### Deprecated:
- `/countries/[country_name]`
gives the entire data of a given country with a start and end date. (OLD)
- `/countries`
gives a list of countries and their latitude and longitude