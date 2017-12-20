from .utils import get_food_info_for_today, get_food_info_for_tomorrow
from nom_track_app.app import app


def slack_get_info_for_date(date, tomorrow):
    if tomorrow:
        data = get_food_info_for_tomorrow(date)
        text = food_sources_to_slack_text(data)
    else:
        data = get_food_info_for_today(date)
        text = food_sources_to_slack_text(data)

    response_dict = food_sources_to_slack_attachments(data)

    return response_dict


def food_sources_to_slack_attachments(data):
    app.logger.info("Building slack response from data: %s", data)

    ret = {
        'text': "Food options for {}".format(data.get('date')),
        'response_type': 'in_channel',
        'attachments': []
    }

    for fs in data.get('food_sources', []):

        yelp = fs.get('yelp_info', {})

        ret['attachments'].append({
            'title': fs['name'],
            'thumb_url': yelp.get('image_url'),
            'title_link': yelp.get('url'),
            'color': 'good',
            # buttons to urls don't seem to work
            # 'actions': [
            #     {
            #         'type': 'button',
            #         'text': 'Menu',
            #         'url': fs['menu'],
            #         'style': 'primary'
            #     }
            # ],
            'fields': [
                {
                    'title': 'Menu',
                    'value': '<{}|View Menu>'.format(fs['menu']),
                    'short': False
                },
                {
                    'title': 'Type',
                    'value': fs['type'],
                    'short': True
                },
                {
                    'title': 'Rating',
                    'value': yelp.get('rating', ''),
                    'short': True
                },
                {
                    'title': 'Cost',
                    'value': yelp.get('cost', ''),
                    'short': True
                },
                {
                    'title': 'Phone',
                    'value': yelp.get('phone', ''),
                    'short': True
                }
            ]
        })

    return ret

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


