from flask import Flask

app = Flask(__name__)


def get_food_trucks_for_day(dt):
    example = {
        "name": "Star Truck",
        "website": "http://example.com",
        "type": "fooda",
        "menu": "http://example.com/menu",
        "yelp_info": {
            "rating": float(5.0),
            "number_of_reviews": int(123),
            "cost": "$$$$$$$$"
        }
    }
    return example


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
