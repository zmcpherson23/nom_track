import dateparser
import requests
import urllib.parse

from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)


def get_food_trucks_for_day(dt):
    desired_date = dt.date()
    app.logger.info('finding food truck events for date="%s"', desired_date)
    # TODO: truck website discovery - Google search?
    # TODO: truck yelp discovery - Google search?
    ft_catering_month_uri = (
        "https://creator.zohopublic.com/greggless"
        "/fulfilling/view-embed/Truck_Schedule"
        "/eSHXxru9GEarMBCkuUG3Z1VEWQzxspZ5nB57YafxhHmVEe3GQAt"
        "FJC7AeHPaxQF7Rz7gbwZWh1W10QywXff6y5vyrasdugJ1hst7"
        "/ID=2158405000001782031&thatdate={}"
    ).format(
        urllib.parse.quote(dt.strftime('%b 01,%Y'))
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
            if truck_date == desired_date:
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


if __name__ == '__main__':
    app.run()
