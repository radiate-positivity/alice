from flask import Flask, request
import logging
import json
import os
import requests
import sys

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s %(levelname)s %(name)s %(message)s')

sessionStorage = {}
V = {'0': 10, 'J': 2, 'Q': 3, 'K': 4, 'A': 11}
@app.route('/post', methods=['POST'])
def main():

    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False ,
            'game_id': None,
            'point': 0
            }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Хочешь поиграть в карты?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Правила',
                    'hide': True
                }
            ]

    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                game_id = start()
                sessionStorage[user_id]['game_id'] = game_id
                sessionStorage[user_id]['game_started'] = True
                #res['response']['text'] = game_id
                p, p_o, card = take(sessionStorage[user_id]['game_id'], sessionStorage[user_id]['point'], res)
                sessionStorage[user_id]['point'] = p
                play_game(res, req)

            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Хорошо, приходите ещё!'
                res['end_session'] = True

            elif 'правила' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Вам произвольно выбирается карта из колоды. Количество очков равно номиналу карты. Туз, король, дама, валет оцениваются как 11, 4, 3, 2. Карты берутся, пока количество набранных очков не равно 21 и более. Если вы набрали раовно 21 очко - вы выиграли, меньше - проиграли.Будем играть?'

            else:
                res['response']['text'] = 'Так ты хочешь сыграть?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    },
                    {
                        'title': 'Правила',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)

def play_game(res, req):
    user_id = req['session']['user_id']
    p, p_o, card = take(sessionStorage[user_id]['game_id'], sessionStorage[user_id]['point'], res)
    sessionStorage[user_id]['point'] = p
    if p == 21:
        res['response']['text'] = 'Вы вытащили {}, это {} очков. Всего у вас 21 очко! Вы выйграли! Хотите сыграть ещё?'.format(card, p_o)
        sessionStorage[user_id]['game_started'] = False
        sessionStorage[user_id]['game_id'] = None
        sessionStorage[user_id]['point'] = 0
    elif p > 21:
        res ['response']['text'] = 'Вы вытащили {}, это {} очков. Всего у вас {}. Вы проиграли:( Хотите сыграть ещё?'.format(card, p_o, p)
        sessionStorage[user_id]['game_started'] = False
        sessionStorage[user_id]['game_id'] = None
        sessionStorage[user_id]['point'] = 0
    else:
        res['response']['text'] = 'Вы вытащили {}, это {} очков. Всего у вас {}. Берём ещё карту?'.format(card, p_o, p)
        res['response']['buttons'] = [
            {
                'title': 'Да',
                'hide': True
            },
            {
                'title': 'Нет',
                'hide': True
            },
            {
                'title': 'Правила',
                'hide': True
            }
        ]
    return


def take(game_id, point, res):
    p_o = None
    card = None
    cards = take_card(game_id)
    card = cards[-1]['code']
    res['response']['text'] = '{}'.format(card)
    if card[0].isdigit() and card[0] != '0':
        p_o = int(card[0])
        point += int(card[0])
    else:
        p_o = V[card[0]]
        point += V[card[0]]
    return point, p_o, card


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)

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

#if __name__ == '__main__':
#    app.run()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
