import json
import os
import random
import re
from datetime import datetime

import config
from bin.get_session_vk_api import get_session_vk_api
from bin.load_base_tokens import load_base_tokens


def get_session():

    session = dict()

    # Пользовательские настройки (из файла config.py)
    session['url_reklama_post'] = config.URL_REKLAMA_POST

    if config.count_members_up_max == 0:
        session['count_members_up_max'] = 1234567890
    else:
        session['count_members_up_max'] = config.count_members_up_max

    if config.count_members_maximum == 0:
        session['count_members_maximum'] = 1234567890
    else:
        session['count_members_maximum'] = config.count_members_maximum

    # Загружаем базу токенов с попытками
    session = load_base_tokens(session)

    # Выбираем имя токена для соединения с ВК
    session['name_work_token'] = random.choice(session['karusel_tokens'])

    # Подсоединяемся к ВК
    session = get_session_vk_api(session)

    # Загружаем список вручную запрещенных ID групп
    try:
        with open(os.path.join("base/main_black_ids.json"), 'r', encoding='utf-8') as f:
            session['main_black_ids'] = json.load(f)
    except:
        session['main_black_ids'] = [0]

    # Загружаем программный список запрещенных ID групп (их нужно раз в три месяца вычищать или сделать
    # фиксированный размер списка и удалять старые при переполнении)
    try:
        with open(os.path.join("base/update_black_ids.json"), 'r', encoding='utf-8') as f:
            session['update_black_ids'] = json.load(f)
    except:
        session['update_black_ids'] = [0]

    # Выставляем счетчики и накопители (настраивать ненужно)
    session['count_rek_posts'] = 0
    session['list_reklama_text'] = []
    session['count_up'] = 0
    session['count_down'] = 0
    session['count_all_members'] = 0
    session['list_url'] = ""
    session['all_found_groups_from_words'] = 0
    session['all_found_groups'] = 0

    # Разбираем адрес на группу и пост для скачивания.
    session['from_group'], session['post_id'] = config.URL_REKLAMA_POST[19:].split('_')
    session['from_group'] = int(session['from_group'])
    session['post_id'] = int(session['post_id'])

    # Получаем текущее время, дату для формирования названия файла отчета
    session['current_date'] = datetime.now().date()
    session['current_time'] = datetime.now().time()

    # Получаем название рекламируемой группы
    session['name_group'] = session['vk_app'].groups.getById(group_ids=abs(session['from_group']),
                                                             fields='description')[0]['name']
    session['name_group'] = re.sub(r"\W", ' ', session['name_group'], 0, re.M | re.I)
    session['name_group'] = re.sub(r'\s+', ' ', session['name_group'], 0, re.M)
    session['name_group'] = re.sub(r'^\s+|\s+$', '', session['name_group'], 0, re.M)

    # Название файла отчета (можно изменить)
    session['name_file'] = f"base/Реклама {session['name_group']} от " \
                           f"{str(session['current_date'])}-{str(session['current_time'].hour)}" \
                           f"-{str(session['current_time'].minute)}.html"

    # Готовим список ключевых слов
    session['list_key_words'] = config.KEY_WORDS.split(",")

    return session
