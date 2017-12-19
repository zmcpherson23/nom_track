import datetime
from .utils import get_food_info_for_day
from nom_track_app.app import app

def get_today():
    today = datetime.datetime.now().date()
    data = get_food_info_for_day(today)
    text = food_sources_to_slack_text(data)

    response_dict = {
        "text": text,
        "response_type": "in_channel"
    }

    return response_dict

def food_sources_to_slack_text(data):
    app.logger.info("Grabbing slack text from info data: %s", data)
    date = data['date']
    output_text = "Date: " + date + " \n"
    food_srcs = data['food_sources']

    for fs in food_srcs:
        type = fs['type']
        name = fs['name']
        menu = fs['menu']

        output_text += type + ": *" + name + "* Menu: " + menu + "\n"
    return output_text

