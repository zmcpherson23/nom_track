import dateparser
import google
import re
import requests
import urllib.parse
import yaml
import os
from pathlib import Path

from datetime import datetime, time

from bs4 import BeautifulSoup
from nom_track_app.app import app, cache
from nom_track_app.app.models import User, UserRating


def load_config():
    dir = os.path.dirname(__file__)
    config_path = os.path.join(Path(dir).parent, "config.yaml")
    with open(config_path, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            app.logger.exception(exc)


def find_yelp_id(truck_name):
    """Get the yelp business id from a truck name

    :truck_name: string representing the name of a truck

    :return: None if no yelp id was found
             str representing the yelp id
    """
    known_yelp_ids = {
        'cousins maine lobster 1':
            'cousins-maine-lobster-los-angeles',
        'the original grilled cheese truck':
            'the-grilled-cheese-truck-los-angeles',
        'vchos':
            'vchos-truck-los-angeles',
        'phantom food truck':
            'phantom-food-truck-los-angeles-2',
        'pastor chef':
            'pastor-chef-asian-and-american-grill-torrance-4'
    }

    yelp_id = known_yelp_ids.get(truck_name.lower())
    if not yelp_id:
        # fallback to google
        google_result = google.search(
            '{} los angeles site:yelp.com'.format(
                truck_name))
        try:
            url = next(google_result)
            # looking for somethin like
            # https://www.yelp.com/biz/vchos-truck-los-angeles
            match = re.search('yelp.com/biz/(.+)', url)
            if match:
                yelp_id = match.group(1)
        except StopIteration:
            yelp_id = None
    return yelp_id


def fetch_yelp_data(yelp_id):
    config_data = load_config()

    yelp_api_url = "https://api.yelp.com/v3/businesses/{}".format(yelp_id)

    headers = {
                    "Authorization": "Bearer {}".format(config_data.get('yelp_api_key')),
                    "Accept": "application/json"
              }

    try:
        yelp_response = requests.get(yelp_api_url,
                                     timeout=240,
                                     headers=headers)
        return yelp_response.json()
    except ConnectionError as ex:
        app.logger.exception(ex)
        return {}


def get_food_info_for_day(date):
    info_dict = {"date": date.isoformat()}
    food_sources = get_food_trucks_for_day(date)
    food_sources.extend(get_fooda_for_day(date))
    info_dict["food_sources"] = food_sources

    return info_dict


@cache.memoize()
def get_fooda_for_day(date):
    items = []

    app.logger.info('finding fooda events for date="%s"', date)

    fooda_init_uri = (
        'https://app.fooda.com'
        '/accounts/3404/popup/menu_page/P0172081/items'
    )

    fooda_uri = (
        'https://app.fooda.com/my?date={}'
        '&filterable%5Baccount_id%5D%5B%5D=3404'
        '&filterable%5Blocations%5D%5Bbuilding_id%5D%5B%5D=3037'
        '&filterable%5Bmeal_period%5D=Lunch'
    ).format(
        urllib.parse.quote(date.isoformat())
    )

    session = requests.Session()

    # hit a url that makes a cookie session pointed at howard hughes
    session.get(fooda_init_uri)

    # hit the url with the exact date we want
    app.logger.info('loading fooda calendar url="%s"', fooda_uri)
    resp = session.get(fooda_uri)
    html = resp.content

    app.logger.debug('fooda today html="%s"', html)

    if re.search('does not have any events', html.decode('utf-8')):
        app.logger.warn(
            'no fooda events for today: redirect to another day detected')
        return items

    # NOTE: the howard hughes HTML is poorly foormed enough that the
    # 'html.parser', 'lxml', or 'xml' parsers are insufficient
    soup = BeautifulSoup(html, 'html5lib')

    events = soup.find_all('a', class_='js-vendor-tile')
    for event in events:
        name = event.find('div', class_='myfooda-event__name').get_text()
        yelp_data = fetch_yelp_data(find_yelp_id(name))
        menu = event.get('href')
        items.append({
            'name': name,
            'date': date.isoformat(),
            'type': 'Fooda',
            'hours': {
                'open': datetime.combine(date, time(11, 30)).isoformat(),
                'close': datetime.combine(date, time(13, 30)).isoformat()
            },
            'menu': menu,
            'yelp_info': {
                "id": yelp_data.get("id", "Not Available"),
                "rating": yelp_data.get("rating", "Not Available"),
                "number_of_reviews": yelp_data.get("review_count", "Not Available"),
                "cost": yelp_data.get("price", "Not Available")
            }
        })

    return items


# implement caching
@cache.memoize()
def get_food_trucks_for_day(date):
    app.logger.info('finding food truck events for date="%s"', date)
    ft_catering_month_uri = (
        "https://creator.zohopublic.com/greggless"
        "/fulfilling/view-embed/Truck_Schedule"
        "/eSHXxru9GEarMBCkuUG3Z1VEWQzxspZ5nB57YafxhHmVEe3GQAt"
        "FJC7AeHPaxQF7Rz7gbwZWh1W10QywXff6y5vyrasdugJ1hst7"
        "/ID=2158405000001782031&thatdate={}"
    ).format(
        urllib.parse.quote(date.strftime('%b 01,%Y'))
    )

    app.logger.info('loading ft calendar url="%s"', ft_catering_month_uri)

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
                name = columns[1].get_text().strip()
                yelp_data = fetch_yelp_data(find_yelp_id(name))
                menu = columns[2].find('a').get('href')
                items.append({
                    'name': name,
                    'date': truck_date.isoformat(),
                    'type': 'Food Truck',
                    'menu': menu,
                    'hours': {
                        'open': datetime.combine(date, time(11)).isoformat(),
                        'close': datetime.combine(date, time(14)).isoformat()
                    },
                    'yelp_info': {
                        "id": yelp_data.get("id", "Not Available"),
                        "rating": yelp_data.get("rating", "Not Available"),
                        "number_of_reviews": yelp_data.get("review_count", "Not Available"),
                        "cost": yelp_data.get("price", "Not Available")
                    }
                })

    return items

def rate_food_source(user_id, food_source, rating):
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5")

    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id)
    rating = user.rate_food(food_source,rating)
    return rating
