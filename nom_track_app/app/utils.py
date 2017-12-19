import dateparser
import google
import re
import requests
import urllib.parse

from bs4 import BeautifulSoup
from nom_track_app.app import app, cache


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
            'phantom-food-truck-los-angeles-2'
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

def get_food_info_for_day(date):
    info_dict = {"date": date.isoformat()}
    food_sources = get_food_trucks_for_day(date)
    # TODO: after bartle implements get fooda
    # food_sources.extend(get_fooda_for_day(date))
    info_dict["food_sources"] = food_sources

    return info_dict

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
                truck_name = columns[1].get_text().strip()
                items.append({
                    'name': truck_name,
                    'date': truck_date.isoformat(),
                    'type': 'hh',
                    'menu': columns[2].find('a').get('href'),
                    'website': 'http://example.com/TODO',
                    'yelp_info': {
                        "id": find_yelp_id(truck_name),
                        "rating": "TODO",
                        "number_of_reviews": "TODO",
                        "cost": "TODO"
                    }
                })

    return items
