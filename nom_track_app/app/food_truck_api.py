import json

from datetime import datetime

from flask import Flask
from flask_cache import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)


# implement caching
@cache.memoize()
def get_food_trucks_for_day(dt):
    example = [
        {
            "date": dt.__str__(),
            "name": "Star Truck",
            "website": "http://example.com",
            "type": "Fooda",
            "menu": "http://example.com/menu",
            "yelp_info": {
                "rating": float(5.0),
                "number_of_reviews": int(123),
                "cost": "$$$$$$$$"
            }
        }
    ]
    return example


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/today', methods=['GET'])
def list_today_options():
    """
    GET to list food trucks of the day.
    :return: Array of food truck hashes
    """
    today = datetime.now().date()
    data = get_food_trucks_for_day(today)
    return json.dumps(data)


if __name__ == '__main__':
    app.run()
