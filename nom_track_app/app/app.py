import dateparser
import json
import requests
import urllib.parse
import logging
import yaml
import sys

from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, Response
from flask import request
from flask_cache import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

@app.before_request
def log_pre_request():
    app.logger.info("recieved %s  %s    client addr: %s", request.method, request.path, request.remote_addr)

@app.after_request
def log_post_request(response):
    app.logger.info("handled  %s  %s    client addr: %s %s", request.method, request.path,
                                                    request.remote_addr, response.status_code)
    return response

# implement caching
@cache.memoize()
def get_food_trucks_for_day(date):
    app.logger.info('finding food truck events for date="%s"', date)
    # TODO: truck website discovery - Google search?
    # TODO: truck yelp discovery - Google search?
    ft_catering_month_uri = (
        "https://creator.zohopublic.com/greggless"
        "/fulfilling/view-embed/Truck_Schedule"
        "/eSHXxru9GEarMBCkuUG3Z1VEWQzxspZ5nB57YafxhHmVEe3GQAt"
        "FJC7AeHPaxQF7Rz7gbwZWh1W10QywXff6y5vyrasdugJ1hst7"
        "/ID=2158405000001782031&thatdate={}"
    ).format(
        urllib.parse.quote(date.strftime('%b 01,%Y'))
    )

    app.logger.info('loading calendar url="%s"', ft_catering_month_uri)

    resp = requests.get(ft_catering_month_uri)
    html = resp.content

    app.logger.debug('calendar html="%s"', html)

    # NOTE: the howard hughes HTML is poorly foormed enough that the
    # 'html.parser', 'lxml', or 'xml' parsers are insufficient
    soup = BeautifulSoup(html, 'html5lib')

    truck_table_rows = soup.find_all(
        'table', class_='trucks'
    )[0].find_all('tr')

    items = []

    truck_date = ''
    for tr in truck_table_rows:

        columns = tr.find_all('td')
        if len(columns) == 1:
            app.logger.debug('date row="%s"', tr)
            truck_date = dateparser.parse(
                tr.find_all('td')[0].get_text()
            ).date()
        elif len(columns) > 1:
            app.logger.debug('truck row="%s"', tr)
            if truck_date == date:
                app.logger.info('truck for desired date found')
                items.append({
                    'name': columns[1].get_text(),
                    'date': truck_date.isoformat(),
                    'type': 'hh',
                    'menu': columns[2].find('a').get('href'),
                    'website': 'http://example.com/TODO',
                    'yelp_info': {
                        "rating": "TODO",
                        "number_of_reviews": "TODO",
                        "cost": "TODO"
                    }
                })

    return items


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
    data = get_food_trucks_for_day(today)
    resp = Response(json.dumps(data))
    resp.headers['Content-Type'] = 'application/json'
    return resp


if __name__ == '__main__':
    app.run()
