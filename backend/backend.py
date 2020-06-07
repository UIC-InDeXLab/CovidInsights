from flask import Flask, jsonify
import loader
import exceptions

app = Flask(__name__)



@app.route('/countries', methods=['GET'])
def get_all_countries():
    return jsonify(loader.country_dict)


# todo: add regions
# todo: add functionality for deaths, confirmed, etc.
@app.route('/countries/<country_name>', methods=['GET'])
def get_country_data(country_name):
    try:
        country_data, start_date = loader.get_country_data(country_name)
    except exceptions.InvalidCountryException:
        return not_found(404)

    return jsonify({
        'country_name': country_name,
        'start_date': start_date,
        'length': len(country_data),
        'confirmed_cases': country_data
    })


@app.route('/get_similar_regions/')
def get_top_k_similar():
    return None


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': {
        'code': 400,
        'message': 'Bad request'
    }}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': {
        'code': 404,
        'message': 'Not found'
    }}), 404


@app.errorhandler(405)
def server_error(error):
    return jsonify({'error': {
        'code': 405,
        'message': 'Method not allowed'
    }}), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': {
        'code': 500,
        'message': 'Server error'
    }}), 500
