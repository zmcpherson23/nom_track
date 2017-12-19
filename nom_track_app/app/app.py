import json
import logging
import sys

from datetime import datetime
from flask import Response, request, jsonify

from nom_track_app.app import app
from .slack import get_today
from .utils import get_food_info_for_day


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


@app.before_request
def log_pre_request():
    app.logger.info("recieved %s  %s    client addr: %s",
                    request.method, request.path, request.remote_addr)


@app.after_request
def log_post_request(response):
    app.logger.info(
        "handled  %s  %s    client addr: %s %s",
        request.method, request.path,
        request.remote_addr, response.status_code)
    return response


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/today', methods=['GET'])
def list_today_options():
    """
    GET to list food trucks of the day.
    :return: Array of food truck hashes
    """
    app.logger.info("Processing /api/today request")
    today = datetime.now().date()
    data = get_food_info_for_day(today)
    resp = Response(json.dumps(data))
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/slack/today', methods=['POST'])
def slack_list_today_options():
    """
    GET to list food trucks of the day.
    :return: Array of food truck hashes
    """
    app.logger.info("Processing /slack/today request")

    return jsonify(get_today())
