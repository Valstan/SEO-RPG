import json
import os

import config


def load_base_tokens(session):
    # Загружаем базу токенов с попытками
    try:
        with open(os.path.join("base/tokens_shuts.json"), 'r', encoding='utf-8') as f:
            session['tokens_shuts'] = json.load(f)
    except:
        session['tokens_shuts'] = {}
    session['tokens'] = {}
    session['karusel_tokens'] = []
    priority = 1
    config.TOKENS.reverse()
    for token_one in config.TOKENS:
        priority *= 2
        for i in range(priority):
            session['karusel_tokens'].append(token_one[0])

        session['tokens'][token_one[0]] = token_one[1]

    return session
