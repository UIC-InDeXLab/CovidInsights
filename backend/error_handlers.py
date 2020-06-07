from backend import app
from flask import jsonify


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': {
        'code': 400,
        'message': 'Bad request'
    }}), 400


@app.errorhandler(404)
def not_found(error):
    return {'error': {
        'code': 404,
        'message': 'Not found'
    }}, 404


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
