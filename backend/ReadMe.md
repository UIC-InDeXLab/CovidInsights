COVID Analysis Backend

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
- `/country_stats/[country_name]` gives the confirmed cases in a country, with it's latitude and longitude
- `/country_stats/list_all_countries` lists all countries
- `/locate/<country_name>` gives lat and long of the given country
- `/compare_countries/<coutry_name>` gives other countries that are similar
to the given country by taking a sample of size = window ending in date specifified in the date parameter.
 Need to pass the following GET parameters:
    - `date=<date:string>` format: `YYYY-MM-DD`. optional. If not given, takes the 
    latest available date in data
    - `window=<window_size:int>` 
    
### Deprecated:
- `/countries/[country_name]`
gives the entire data of a given country with a start and end date. (OLD)
- `/countries`
gives a list of countries and their latitude and longitude