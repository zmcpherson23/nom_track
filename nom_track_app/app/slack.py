import datetime
from .utils import get_food_trucks_for_day

def get_today():
    today = datetime.datetime.now()
    data = get_food_trucks_for_day(today)
    text = food_sources_to_slack_text(data)

    response_dict = {
        "text": text,
        "response_type": "in_channel"
    }

    return response_dict

def food_sources_to_slack_text(data):
    date = data['date']
    output_text = "Date: " + date + " \n"
    food_srcs = data['food_sources']

    for fs in food_srcs:
        type = fs['type']
        name = fs['name']
        menu = fs['menu']

        output_text += type + ": *" + name + "* Menu: " + menu + "\n"
    print(output_text)
    return output_text

