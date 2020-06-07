from flask import Flask, jsonify, request
import loader
import exceptions
from backend import app

# app = Flask(__name__)
# app.debug = True

@app.route('/countries', methods=['GET'])
def get_all_countries():
    return jsonify(loader.country_dict)

# todo: add regions
# todo: add functionality for deaths, confirmed, etc.
@app.route('/countries/<country_name>', methods=['GET'])
def get_country_data(country_name):
    try:
        country_data, start_date, end_date = loader.get_country_data(country_name)
    except exceptions.InvalidCountryException:
        return not_found(404)

    return jsonify({
        'country_name': country_name,
        'start_date': start_date,
        'end_date': end_date,
        'length': len(country_data),
        'confirmed_cases': country_data
    })


@app.route('/get_similar_regions/')
def get_top_k_similar():
    return None