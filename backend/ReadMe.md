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
- /countries
gives a list of countries and their latitude and longitude
- /country_stats/[country_name] gives the confirmed cases in a country, with it's latitude and longitude

deprecated:
- /countries/[country_name]
gives the entire data of a given country with a start and end date. (OLD)