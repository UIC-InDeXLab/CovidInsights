from backend import app
from flask import jsonify

invalid_country_msg = "Invalid country name. Please check using /list/countries to see valid country names."
invalid_region_msg = "Invalid region name. Please check using /list/regions to see names of regions."
invalid_country_or_no_regions_msg = "Country name invalid or this country doesn't have regional data. " \
    "Refer to /list/countries and /list/regions"
invalid_window_msg = "A GET parameter 'window' must be provided such that: "\
    "1 <= window <= (number of days available in data)"
invalid_type_msg = "GET parameter 'type' should be one of: 'deaths', 'recovered', 'cases'. Default is 'cases'."
invalid_date_fmt = "GET parameter 'date' either invalid or not in format YYYY-MM-DD."
date_out_of_range = "Provided date is out of range of data available."


@app.errorhandler(400)
def bad_request(error):
    return {'error': {
        'code': 400,
        'message': error.description
    }}, 400


@app.errorhandler(404)
def not_found(error):
    return {'error': {
        'code': 404,
        'message': error.description
    }}, 404


@app.errorhandler(405)
def server_error(error):
    return {'error': {
        'code': 405,
        'message': error.description
    }}, 405


@app.errorhandler(500)
def server_error(error):
    return {'error': {
        'code': 500,
        'message': error.description
    }}, 500
