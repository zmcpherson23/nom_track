from .utils import get_food_info_for_day, rate_food_source
from nom_track_app.app import app


def slack_get_info_for_date(date):
    data = get_food_info_for_day(date)
    text = food_sources_to_slack_text(data)

    response_dict = {
        "text": text,
        "response_type": "in_channel",
        "unfurl_media": False
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
        rating = fs['yelp_info']['rating']

        output_text += type + ": *" + name + "* <" + menu + "|Menu> Rating: " + str(rating) + "\n"

    return output_text

def slack_rate_food(user_id, food_source, rating):
    rating = int(rating)
    if not rating or rating < 1 or rating > 5:
        text = "Rating needs to be between 1 and 5"
    else:
        user_rating = rate_food_source(user_id, food_source, rating)
        text = "You rated *" + user_rating.food_source + "* a *" + str(user_rating.rating) + "*!\n"

    response_dict = {
        "text": text,
        "response_type": "in_channel"
    }

    return response_dict