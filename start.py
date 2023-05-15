import json
import os
import random
import re
import time
from datetime import datetime

from vk_api import VkApi, VkTools

import config
from check_token_limit import count_limit_tokens


def save_result(session):
    print(f"Опубликовано - {session['count_up']}. Пропущено - {session['count_down']}. "
          f"Обработал {session['count_up'] + session['count_down']} из {session['all_found_groups']}.")

    result = f"""<html>
            <head>
            <title>Title</title>
            </head>
            <body>
            <h2>Кого или что рекламируем: {config.name_reklama}</h2>
            <h2>Адрес рекламируемого поста: <a href="{config.URL_REKLAMA_POST}">{config.URL_REKLAMA_POST}</a></h2>
            Список ключевых слов поиска:<br />
            {session['list_key_words']}<br />
            Подпись-ссылка в группу: {config.url_reklama}. Сделать {config.count_post_up_max} размещений.<br />
            Диапазон количества подписчиков в группе:<br />
            Мин - {config.count_members_minimum}, Макс - {config.count_members_maximum}, Всего - {config.count_members_up_max}<br />
            <h2>Всего найдено: {session['all_found_groups']} групп.<br />
            Обработано {session['count_up'] + session['count_down']} групп<br />
            Успешно размещено {session['count_up']} объявлений для {session['count_all_members']} подписчиков.<br />
            {session['count_down']} групп отсеяно за негодностью.<br />
            <h2>Список ссылок на группы в которые удалось разместить объявление:</h2>
            <p>{session['list_url']}</p>
            <br /> <br /> <br /> <br />       
            </body>
            </html>
            """

    with open(os.path.join(session['name_file']), 'w', encoding='utf-8') as f:
        f.write(result)


def get_attach(msg):
    if 'attachments' in msg:
        attach = ''
        for sample in msg['attachments']:
            type_attach = sample['type']
            if type_attach == 'link':
                return sample[type_attach]['url']
            elif type_attach == 'photos_list':
                attach += ''.join(map(str, (type_attach, sample[type_attach], ',')))
            else:
                attach += ''.join(map(str, (type_attach, sample[type_attach]['owner_id'],
                                            '_', sample[type_attach]['id'], ',')))
        return attach[:-1]
    else:
        return ''


def get_reklama_post(session):
    # Получаем пост, который будем рекламировать.
    reklama_posts = session['vk_app'].wall.get(owner_id=session['from_group'], count=100, offset=0)['items']

    # Находим нужный нам пост по его ID
    for sample in reklama_posts:
        if sample['id'] == session['post_id']:

            # Забираем картинки
            session['reklama_attachments'] = get_attach(sample)

            # Если нужна подпись под текстом, добавляем её
            if config.url_reklama:
                sample[
                    'text'] = f"{sample['text']}\n\n{config.signature_after} @https://vk.com/public{abs(session['from_group'])} (\"{session['name_group']}\") {config.signature_before}."

            # Берем первый чистый текст в список текстов
            session['list_reklama_text'].append(sample['text'])

            # Набираем следующие тексты с измененными буквами на латиницу
            for i in range(0, len(config.letter_sub[0]) - 1):
                session['list_reklama_text'].append(
                    f"{re.sub(config.letter_sub[0][i], config.letter_sub[1][i], sample['text'], 0, re.M)}")

            return session


def get_sort_groups(session):
    for keyword_namefile in session['list_key_words']:
        try:
            with open(os.path.join(f"base/{keyword_namefile}_база_id.json"), 'r', encoding='utf-8') as f:
                session['region_base'].update(json.load(f))
        except:
            print(f"По ключевому слову поиска - '{keyword_namefile}'"
                  f" нет базы данных ID групп, сначала создай ее скриптом update_groups_base_by_keys.py")
            quit()

    # Перемешиваем список ID или наоборот сортируем от самой большой группы к маленькой
    if config.group_shuffle:
        keys = list(session['region_base'].keys())
        random.shuffle(keys)
        shuffle_dict = dict()
        for key in keys:
            shuffle_dict.update({key: session['region_base'][key]})
        session['region_base'] = shuffle_dict
    else:
        session['region_base'] = dict(sorted(session['region_base'].items(), key=lambda item: item[1], reverse=True))

    session['all_found_groups'] = len(session['region_base'])

    return session


def post_in_sort_groups(session):

    for true_group_id, count_members in session['region_base'].items():

        true_group_id = abs(int(true_group_id))

        if true_group_id in session['main_black_ids'] or true_group_id in session['redaktor_black_ids']:
            session['count_down'] += 1
            continue

        session = checking_token_limit(session)
        if not session:
            print("Кончились токены, сорян...")
            return

        session['count_rek_posts'] += 1
        if session['count_rek_posts'] == len(session['list_reklama_text']):
            session['count_rek_posts'] = 0

        try:
            session['vk_app'].wall.post(owner_id=-true_group_id,
                                        from_group=0,
                                        message=session['list_reklama_text'][session['count_rek_posts']],
                                        attachments=session['reklama_attachments'])

            session['count_all_members'] += count_members

            session['list_url'] += \
                f"""<a href="https://vk.com/public{true_group_id}">https://vk.com/public{true_group_id} - {count_members} подписчиков</a><br />"""

            print(
                f"https://vk.com/public{true_group_id} - {count_members} подписчиков. "
                f"Всего - {session['count_all_members']}")

            session['count_up'] += 1

            curr_dt = datetime.now()
            session['shut_token'].append(int(round(curr_dt.timestamp())))
            if len(session['shut_token']) > 100:
                del session['shut_token'][0]
            with open(os.path.join(f"base/{session['tokens'][0][0]}_shut_token.json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(session['shut_token'], indent=2, ensure_ascii=False))

            save_result(session)

            if session['count_up'] > session['count_post_up_max']:
                return
            if session['count_all_members'] > session['count_members_up_max']:
                return

            time.sleep(random.randint(3, 7))

        except Exception as ext:
            print(ext)
            if "user should be group editor" in str(ext) or "Access denied" in str(ext):
                session['redaktor_black_ids'].append(true_group_id)
                with open(os.path.join("base/redaktor_black_ids.json"), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(session['redaktor_black_ids'], indent=2, ensure_ascii=False))
            if "Too many recipients" in str(ext):
                save_result(session)
                return
            session['count_down'] += 1
            time.sleep(5)

    return session


def get_session_vk_api(session):
    for i in range(3):
        if session['token']:
            try:
                vk_session = VkApi(token=session['token'])
                session['vk_app'] = vk_session.get_api()
                session['tools'] = VkTools(vk_session)
                return session
            except Exception as exc:
                print(exc)
        else:
            try:
                vk_session = VkApi(session['login'], session['password'])
                vk_session.auth()
                session['vk_app'] = vk_session.get_api()
                session['tools'] = VkTools(vk_session)
                return session
            except Exception as exc:
                print(exc)
    return session


def get_session(session):
    # Пользовательские настройки (из файла config.py)
    session['url_reklama_post'] = config.URL_REKLAMA_POST
    session['count_post_up_max'] = config.count_post_up_max
    if config.count_members_up_max == 0:
        session['count_members_up_max'] = 1234567890
    else:
        session['count_members_up_max'] = config.count_members_up_max
    session['count_members_minimum'] = config.count_members_minimum
    if config.count_members_maximum == 0:
        session['count_members_maximum'] = 1234567890
    else:
        session['count_members_maximum'] = config.count_members_maximum

    # Загружаем список вручную запрещенных ID групп
    try:
        with open(os.path.join("base/main_black_ids.json"), 'r', encoding='utf-8') as f:
            session['main_black_ids'] = json.load(f)
    except:
        session['main_black_ids'] = [0]

    # Загружаем список автоматических запрещенных ID групп (их нужно раз в три месяца вычищать или сделать
    # фиксированный размер списка и удалять старые при переполнении
    try:
        with open(os.path.join("base/redaktor_black_ids.json"), 'r', encoding='utf-8') as f:
            session['redaktor_black_ids'] = json.load(f)
    except:
        session['redaktor_black_ids'] = [0]

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

    # Создаем ГЛОБАЛЬНУЮ базу - словарь списка ID групп
    session['region_base'] = {}

    return session


def karusel_tokens():
    session = dict()
    session['tokens'] = []
    # Собираем карусель токенов
    if config.TOKEN_VK_API_1:
        session['tokens'].append([config.TOKEN_VK_API_1_name, config.TOKEN_VK_API_1])
    if config.TOKEN_VK_API_2:
        session['tokens'].append([config.TOKEN_VK_API_2_name, config.TOKEN_VK_API_2])
    if config.TOKEN_VK_API_3:
        session['tokens'].append([config.TOKEN_VK_API_3_name, config.TOKEN_VK_API_3])
    if config.TOKEN_VK_API_4:
        session['tokens'].append([config.TOKEN_VK_API_4_name, config.TOKEN_VK_API_4])
    if config.TOKEN_VK_API_5:
        session['tokens'].append([config.TOKEN_VK_API_5_name, config.TOKEN_VK_API_5])
    return session


def checking_token_limit(session):
    while True:
        if not session['shut_token']:
            session['token'] = session['tokens'][0][1]

            try:
                with open(os.path.join(f"base/{session['tokens'][0][0]}_shut_token.json"), 'r', encoding='utf-8') as f:
                    session['shut_token'] = json.load(f)
            except:
                session['shut_token'] = [1643164102]  # Старая дата где-то из 2022 года
                with open(os.path.join(f"base/{session['tokens'][0][0]}_shut_token.json"), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(session['shut_token'], indent=2, ensure_ascii=False))
            # Подключаемся к API VK
            session = get_session_vk_api(session)

        limit = config.token_limit + 1
        curr_dt = datetime.now()
        time_day_ago = int(round(curr_dt.timestamp())) - 90000
        for i in session['shut_token']:
            if i > time_day_ago:
                limit -= 1

        if limit < 0:
            session['shut_token'] = []
            del session['tokens'][0]
            if not session['tokens']:
                print("!!! У всех токенов закончился лимит на публикации.")
                return
            else:
                continue
        else:
            return session


if __name__ == '__main__':
    # Сверим аппетиты рекламщика и возможности токенов
    last_limit_token = count_limit_tokens(config.token_limit)
    print(f"Токенов осталось на {last_limit_token} раз, а реклам заказал на {config.count_post_up_max} раз. ")
    sess = karusel_tokens()
    sess['shut_token'] = []
    sess = checking_token_limit(sess)
    if sess:
        # Подгружаем пользовательские настройки
        sess = get_session(sess)
        sess = get_reklama_post(sess)
        sess = get_sort_groups(sess)
        sess = post_in_sort_groups(sess)

    print("Работа программы SEO-RPG завершена!")
