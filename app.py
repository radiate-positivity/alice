from flask import Flask, request
import logging
import json
from trans import *

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')

sessionStorage = {}
V = {'0': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
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
            'who_go': 0,
            'best_card': choise(['H', 'C', 'D', 'S'])
            }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Хочешь поиграть в карта?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]

   if not sessionStorage[user_id]['game_started']:
        if 'да' in req['request']['nlu']['tokens']:
            game_id = start()
            sessionStorage[user_id]['game_id'] = game_id
            print(game_id)
            sessionStorage[user_id]['game_started'] = True

        elif 'нет' in req['request']['nlu']['tokens']:
            res['response']['text'] = 'Ну и как так? Зачем вы тогда приходили?'
            res['end_session'] = True
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
                }
            ]
    else:
        if sessionStorage[user_id]['who_go'] % 2 == 0: # player
            go_player()
        else:
            go_alice()
        sessionStorage[user_id]['who_go'] += 1


def go_player(req):
    pass

def go_alice(req):
    game_id = sessionStorage[user_id]['game_id']
    best =  sessionStorage[user_id]['best_card']
    table = get_cards(game_id, 'table')
    last = table[0][-1]['code']
    alice_card = [x['code'] for x in get_cards(game_id, 'alice')[0]]

    if table[1] % 2 == 1:
        for x in alice_card:
            if x[-1] == last[-1] and last[-1] != best:
                if x[0]


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)

#if __name__ == '__main__':
#    app.run()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


