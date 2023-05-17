import json
import os
import random

import config


def get_sort_groups(session):
    session['base'] = []
    for keyword_namefile in session['list_key_words']:
        try:
            with open(os.path.join(f"base/{keyword_namefile}_база_id.json"), 'r', encoding='utf-8') as f:
                session['base'] += json.load(f)

        except:
            print(f"По ключевому слову поиска - '{keyword_namefile}'"
                  f" нет базы данных ID групп, сначала создай ее скриптом update_groups_base_by_keys.py")
            quit()

    # Перемешиваем список ID или наоборот сортируем от самой большой группы к маленькой
    if config.group_shuffle:
        random.shuffle(session['base'])
    else:
        session['base'] = sorted(session['base'], key=lambda item: item[1], reverse=True)

    session['all_found_groups'] = len(session['base'])

    return session
