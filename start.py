import json
import os
import random
import re
import time
from datetime import datetime
from random import shuffle

from vk_api import VkApi, VkTools

import config


def save_result(session):
    print(f"Опубликовано - {session['count_up']}. Пропущено - {session['count_down']}. "
          f"Обработал {session['count_up'] + session['count_down']} из {session['all_found_groups']}.")

    result = f"""<html>
            <head>
            <title>Title</title>
            </head>
            <body>
            <h2>Адрес рекламируемого поста: <a href="{config.URL_REKLAMA_POST}">{config.URL_REKLAMA_POST}</a></h2>
            <h2>Список ключевых слов поиска:</h2>
            <p>{session['rpg_words']}</p>
            <p>Подпись-ссылка в группу: {config.url_reklama}. Сделать {config.count_post_up_max} размещений.</p>
            <p>Подписоты в группе: Мин - {config.count_members_minimum}, Макс - {config.count_members_maximum}, Всего - {config.count_members_up_max}</p>
            <h2>Всего найдено: {session['all_found_groups']} групп.</h2>
            <p>Обработано {session['count_up'] + session['count_down']} групп</p>
            <p>Успешно размещено {session['count_up']} объявлений для {session['count_all_members']} подписчиков.</p>
            <p>{session['count_down']} групп отсеяно за негодностью.</p>
            <p></p>
            <h2>Список ссылок на группы в которые удалось разместить объявление:</h2>
            <p></p>
            <p>{session['list_url']}</p>
            <p></p>            
            <p></p>            
            <p></p>            
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
            # Берем первый чистый текст
            if config.url_reklama:
                session['list_reklama_text'] = [
                    f"{sample['text']}\n\nВ нашем сообществе @https://vk.com/public{abs(session['from_group'])} (\"{session['name_group']}\") есть еще."]
            else:
                session['list_reklama_text'].append(sample['text'])
            # Набираем следующие тексты с измененными буквами на латиницу
            for i in range(0, len(config.letter_sub[0])-1):
                if config.url_reklama:
                    session['list_reklama_text'].append(
                        f"{re.sub(config.letter_sub[0][i], config.letter_sub[1][i], sample['text'], 0, re.M)}\n\nВ нашем сообществе @https://vk.com/public{abs(session['from_group'])} (\"{session['name_group']}\") есть еще.")
                else:
                    session['list_reklama_text'].append(f"{re.sub(config.letter_sub[0][i], config.letter_sub[1][i], sample['text'], 0, re.M)}")
            session['reklama_attachments'] = get_attach(sample)
            return session


def get_sort_groups(session):
    # Загружаем базы данных с отсеянными прошлые разы группами.
    # Загружаем ОБЩИЙ ЧЕРНЫЙ список
    try:
        with open(os.path.join("base/false_groups_id.json"), 'r', encoding='utf-8') as f:
            session['false_groups_id'] = json.load(f)
    except:
        session['false_groups_id'] = [0]
        with open(os.path.join("base/false_groups_id.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['false_groups_id'], indent=2, ensure_ascii=False))

    # Загружаем БАЗУ РЕГИОНАЛЬНУЮ по настройкам (ключевые слова поиска и ограничения количества подписчиков в группах)
    try:
        with open(os.path.join(session['name_file_region_base']), 'r', encoding='utf-8') as f:
            session['region_base'] = json.load(f)
    except:
        session['region_base'] = {"false_groups_id_by_count_members": [0], "true_groups_id": [167381590],
                                  "rpg_words": session['rpg_words']}
        with open(os.path.join(session['name_file_region_base']), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['region_base'], indent=2, ensure_ascii=False))

    session['region_base']['true_groups_id'].append(167381590)  # Для страховки от пустого списка моя группа ПарсерТест
    session['false_groups_id'].append(0)  # Для страховки от пустого списка
    session['rpg_black_ids'].append(0)  # Для страховки от пустого списка

    session['false_groups_id'].extend(session['rpg_black_ids'])
    session['false_groups_id'].extend(session['region_base']['false_groups_id_by_count_members'])
    session['region_base']['true_groups_id'] = list(
        set(session['region_base']['true_groups_id']).difference(set(session['false_groups_id'])))
    shuffle(session['region_base']['true_groups_id'])

    for value in session['region_base']['rpg_words'].values():
        session['all_found_groups_from_words'] += value

    session['all_found_groups'] = len(session['region_base']['true_groups_id'])

    return session


def post_in_sort_groups(session):
    shuffle(session['region_base']['true_groups_id'])

    for true_group_id in session['region_base']['true_groups_id']:

        session = checking_token_limit(session)
        if not session:
            return

        session['count_rek_posts'] += 1
        if session['count_rek_posts'] == len(session['list_reklama_text']):
            session['count_rek_posts'] = 0

        try:
            session['vk_app'].wall.post(owner_id=-abs(true_group_id),
                                        from_group=0,
                                        message=session['list_reklama_text'][session['count_rek_posts']],
                                        attachments=session['reklama_attachments'])

            time.sleep(1)
            # Получаем количество подписчиков в группе
            count_members = session['vk_app'].groups.getMembers(group_id=abs(true_group_id))['count']

            session['count_all_members'] += count_members

            session['list_url'] += \
                f"""<a href="https://vk.com/public{abs(true_group_id)}">https://vk.com/public{abs(true_group_id)} - {count_members} подписчиков</a><br />"""

            print(
                f"https://vk.com/public{abs(true_group_id)} - {count_members} подписчиков. "
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
            if str(ext) in "Too many recipients":
                save_result(session)
                return
            session['count_down'] += 1
            session['false_groups_id'].append(abs(true_group_id))
            with open(os.path.join("base/false_groups_id.json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(session['false_groups_id'], indent=2, ensure_ascii=False))
            time.sleep(5)

    return session


def search_new_group(session):
    # Поиск новых групп по ключевым словам региона, если еще остались попытки постов до лимита
    session['list_groups'] = []
    for key in session['region_base']['rpg_words'].keys():
        new_groups = session['tools'].get_all(method='groups.search', max_count=1000, limit=session['group_count_max'],
                                              values={'q': key, 'type': 'group'})['items']

        session['region_base']['rpg_words'][key] = len(new_groups)
        session['list_groups'].extend(new_groups)

    for value in session['region_base']['rpg_words'].values():
        session['all_found_groups_from_words'] += value

    session['list_groups'] = [dict(t) for t in {tuple(d.items()) for d in session['list_groups']}]

    session['all_found_groups'] = len(session['list_groups'])

    save_result(session)
    shuffle(session['list_groups'])

    return session


def post_in_new_groups(session):
    for group in session['list_groups']:

        session = checking_token_limit(session)
        if not session:
            return

        # Черный список групп куда постить ненужно
        if group['id'] in session['false_groups_id']:
            session['count_down'] += 1
            continue

        if group['id'] in session['region_base']['true_groups_id']:
            continue

        if 'can_post' in group and group['can_post'] == 0:
            session['false_groups_id'].append(abs(group['id']))
            session['count_down'] += 1
            continue
        if 'wall' in group and group['wall'] != 1:
            session['false_groups_id'].append(abs(group['id']))
            session['count_down'] += 1
            continue
        try:
            if group['is_closed'] != 0 or group['is_advertiser'] == 1 or 'deactivated' in group:
                session['false_groups_id'].append(abs(group['id']))
                session['count_down'] += 1
                continue
        except Exception as ext:
            session['false_groups_id'].append(abs(group['id']))
            session['count_down'] += 1
            print(f"Непонятная ситуация с ключами, пропускаем группу. Ошибка вот: {ext}")
            continue

        try:
            members = session['vk_app'].groups.getMembers(group_id=abs(group['id']))
            if members['count'] > session['count_members_maximum'] or members['count'] < session[
                'count_members_minimum']:
                session['region_base']['false_groups_id_by_count_members'].append(abs(group['id']))
                with open(os.path.join(session['name_file_region_base']), 'w',
                          encoding='utf-8') as f:
                    f.write(json.dumps(session['region_base'], indent=2, ensure_ascii=False))
                session['count_down'] += 1
                continue
        except Exception as ext:
            print(ext)
            session['false_groups_id'].append(abs(group['id']))
            session['count_down'] += 1
            continue

        # Сохраняем все неудачные попытки, так как их больше может не быть
        with open(os.path.join("base/false_groups_id.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['false_groups_id'], indent=2, ensure_ascii=False))

        session['count_rek_posts'] += 1
        if session['count_rek_posts'] == len(session['list_reklama_text']):
            session['count_rek_posts'] = 0

        try:
            session['vk_app'].wall.post(owner_id=-abs(group['id']),
                                        from_group=0,
                                        message=session['list_reklama_text'][session['count_rek_posts']],
                                        attachments=session['reklama_attachments'])

            time.sleep(1)
            session['count_all_members'] += members['count']

            session['list_url'] += \
                f"""<a href="https://vk.com/{group['screen_name']}">https://vk.com/{group['screen_name']} - {members['count']} подписчиков</a><br />"""
            print(
                f"{group['screen_name']} - {members['count']} подписчиков. Всего - {session['count_all_members']}")

            session['region_base']['true_groups_id'].append(abs(group['id']))
            with open(os.path.join(session['name_file_region_base']), 'w',
                      encoding='utf-8') as f:
                f.write(json.dumps(session['region_base'], indent=2, ensure_ascii=False))

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
            session['count_down'] += 1

            if str(ext) in "Too many recipients":
                save_result(session)
                return

            session['false_groups_id'].append(abs(group['id']))
            with open(os.path.join("base/false_groups_id.json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(session['false_groups_id'], indent=2, ensure_ascii=False))
            time.sleep(5)

    save_result(session)


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
    session['group_count_max'] = config.group_count_max
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

    # Составляем список запрещенных ID групп, удаляем у них минус
    session['rpg_black_ids'] = []
    for i in config.RPG_BLACK_IDS:
        session['rpg_black_ids'].append(abs(i))

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
    session['rpg_words'] = {}
    list_key_words = config.KEY_WORDS.split(",")
    for i in list_key_words:
        session['rpg_words'][i] = 0

    session['name_file_region_base'] = f"base/{''.join(list_key_words)}" \
                                       f"_{session['count_members_minimum']}_" \
                                       f"{session['count_members_maximum']}.json"

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

        limit = 60  # Последний лимит знаю что 80 был
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
    sess = karusel_tokens()
    sess['shut_token'] = []
    sess = checking_token_limit(sess)
    if sess:
        # Подгружаем пользовательские настройки
        sess = get_session(sess)
        sess = get_reklama_post(sess)
        sess = get_sort_groups(sess)
        sess = post_in_sort_groups(sess)
        if sess:
            sess = search_new_group(sess)
            post_in_new_groups(sess)

    print("Работа программы SEO-RPG завершена!")
