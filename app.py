import requests
import json
import logging
import os
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

@app.route('/')
@app.route('/index')
def index():
    return "Hello!"

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

    handle_dialog(request.json, response)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                {'title': "Да", 'hide': True},
                {'title': "Нет", 'hide': True}
            ]
        }
        res['response']['text'] = 'Привет!'
        res['response']['buttons'] = sessionStorage[user_id]['suggests']
        return

    response = requests.get('https://deckofcardsapi.com/api/deck/new/shuffle/').json()
    res['response']['text'] = str(response)
    return

#     if req['request']['original_utterance'].lower() in [
#         'ладно',
#         'куплю',
#         'покупаю',
#         'хорошо'
#     ]:
#         res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
#         res['response']['end_session'] = True
#         return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


