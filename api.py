import requests

def start():
    url = 'https://deckofcardsapi.com/api/deck/new/shuffle/'
    response = requests.get(url)
    json = response.json()

    return json['deck_id']

def take_card(deck_id):
    url = 'https://deckofcardsapi.com/api/deck/{}/draw/?count=1'.format(deck_id)

    response = requests.get(url)
    json = response.json()

    return json['cards']
