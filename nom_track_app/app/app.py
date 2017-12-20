import json
import logging
import sys

from datetime import datetime, timedelta
from flask import Response, request, redirect, jsonify, url_for, render_template

from nom_track_app.app import app, models
from .slack import slack_get_info_for_date, slack_rate_food
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


@app.route('/api/<ymd>', methods=['GET'])
def list_date_options(ymd):
    app.logger.info("Processing /api/{} request".format(ymd))
    date = datetime.strptime(ymd, '%Y-%m-%d').date()
    data = get_food_info_for_day(date)
    resp = Response(json.dumps(data))
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/api/today', methods=['GET'])
def list_today_options():
    app.logger.info("Processing /api/today request")
    today = datetime.now().date()
    return redirect(url_for('list_date_options', ymd=today.isoformat()))


@app.route('/api/tomorrow', methods=['GET'])
def list_tomorrow_options():
    app.logger.info("Processing /api/tomorrow request")
    tomorrow = datetime.now().date() + timedelta(days=1)
    return redirect(url_for('list_date_options', ymd=tomorrow.isoformat()))


@app.route('/slack', methods=['POST'])
def slack_list_today_options():
    """
    GET to list food trucks of the day.
    :return: Array of food truck hashes
    """
    app.logger.info("Processing /slack/today request")

    form_data = request.form
    app.logger.info("Form data: %s", form_data)
    text = form_data.get('text')
    date = datetime.now().date()

    if text == 'mothatrucka':
        return jsonify({"text": "https://i.imgur.com/trUUslk.jpg", "response_type": "in_channel"})

    if text.split() and text.split()[0] == 'rate':
        user_id = form_data.get('user_id')
        args = text.split(maxsplit=2)
        rating = args[1]
        food_source = args[2]

        return jsonify(slack_rate_food(user_id, food_source, rating))


    if text == 'tomorrow':
        date = date + timedelta(days=1)

    return jsonify(slack_get_info_for_date(date))


# Homepage
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")