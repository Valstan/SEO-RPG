import json
import os
import random
import re
from datetime import datetime

import config
from bin.get_session_vk_api import get_session_vk_api
from bin.load_base_tokens import load_base_tokens
from bin.load_bases import load_bases


def get_session():
    session = dict()

    # Пользовательские настройки (из файла config.py)
    if config.count_members_up_max == 0:
        session['count_members_up_max'] = 99999999
    else:
        session['count_members_up_max'] = config.count_members_up_max

    if config.count_members_maximum == 0:
        session['count_members_maximum'] = 99999999
    else:
        session['count_members_maximum'] = config.count_members_maximum

    # Загружаем базу токенов с попытками
    session = load_base_tokens(session)

    # Выбираем имя токена для соединения с ВК
    session['name_work_token'] = random.choice(session['karusel_tokens'])

    # Подсоединяемся к ВК
    session = get_session_vk_api(session, vkapp=True)

    # Загружаем базы белых и черных списков ID
    session['base_ids'], session['main_black_ids'], session['update_black_ids'] = load_bases()

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

    # Получаем текущее время, дату для отчета
    month_list = ['0', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    current_date = datetime.now()
    session['data_work'] = f"{current_date.day} {month_list[current_date.month]} {current_date.year}"

    # Получаем название рекламируемой группы
    session['name_group'] = session['vk_app'].groups.getById(group_ids=abs(session['from_group']),
                                                             fields='description')[0]['name'][:25]

    session['name_group'] = re.sub(r"\W", ' ', session['name_group'], 0, re.M | re.I)
    session['name_group'] = re.sub(r'\s+', ' ', session['name_group'], 0, re.M)
    session['name_group'] = re.sub(r'^\s+|\s+$', '', session['name_group'], 0, re.M)

    # Название файла отчета (можно изменить)
    session['name_file'] = f"base/{current_date.strftime('%y%m%d%H%M')} " \
                           f"Реклама {session['name_group']} от {session['data_work']}.html"

    # Готовим список ключевых слов
    session['list_key_words'] = config.KEY_WORDS.split(",")

    return session
