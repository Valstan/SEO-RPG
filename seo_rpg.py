import json
import os
import random
import time
from random import shuffle

from vk_api import VkApi, VkTools

import global_config


def save_result(session):
    print(f"Опубликовано - {session['count_up']}. Пропущено - {session['count_down']}. "
          f"Обработал {session['count_up'] + session['count_down']} из {session['all_found_groups']}.")

    result = f"""<html>
            <head>
            <title>Title</title>
            </head>
            <body>
            <h2>Список ключевых слов поиска и количество найденных по ним групп:</h2>
            <p>{session['rpg_words']}</p>
            <p>Всего найдено по словам - {session['all_found_groups_from_words']} групп.</p>
            <p>Всего найдено реально - {session['all_found_groups']} групп.</p>
            <p>Обработал {session['count_up'] + session['count_down']} групп</p>
            <p>Успешно размещено {session['count_up']} объявлений для {session['count_all_members']} подписчиков.</p>
            <p>Пропущено по тем или иным причинам {session['count_down']} групп.</p>
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

    if session['count_false_groups_id'] != len(session['false_groups_id']):
        with open(os.path.join('false_groups_id.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['false_groups_id'], indent=2, ensure_ascii=False))
        session['count_false_groups_id'] = len(session['false_groups_id'])

    if session['count_true_groups_id'] != len(session['true_groups_id']):
        with open(os.path.join('true_groups_id.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps(session['true_groups_id'], indent=2, ensure_ascii=False))
        session['count_true_groups_id'] = len(session['true_groups_id'])


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
    sample = {}
    for sample in reklama_posts:
        if sample['id'] == session['post_id']:
            break

    session['reklama_text'] = f"{sample['text']}\n\nПодпишись " \
                              f"на @https://vk.com/public{-session['from_group']} ({session['name_group']}), " \
                              f"чтобы ничего не пропустить."
    session['reklama_attachments'] = get_attach(sample)
    return session


def get_sort_groups(session):
    # Загружаем базы данных с отсеянными прошлые разы группами
    with open(os.path.join('rpg_black_ids.json'), 'r', encoding='utf-8') as f:
        session['rpg_black_ids'] = json.load(f)
    with open(os.path.join('false_groups_id.txt'), 'r', encoding='utf-8') as f:
        session['false_groups_id'] = json.load(f)
    with open(os.path.join('true_groups_id.txt'), 'r', encoding='utf-8') as f:
        session['true_groups_id'] = json.load(f)

    session['true_groups_id'].append(-28534711)  # Для страховки от пустого списка
    session['false_groups_id'].append(0)  # Для страховки от пустого списка
    session['rpg_black_ids'].append(0)  # Для страховки от пустого списка

    session['false_groups_id'].extend(session['rpg_black_ids'])
    session['true_groups_id'] = list(
        set(session['true_groups_id']).difference(set(session['false_groups_id'])))
    shuffle(session['true_groups_id'])
    return session


def post_in_sort_groups(session):
    for true_group_id in session['true_groups_id']:
        if true_group_id > 0:
            true_group_id = -true_group_id
        try:
            session['vk_app'].wall.post(owner_id=true_group_id,
                                        from_group=0,
                                        message=session['reklama_text'],
                                        attachments=session['reklama_attachments'])

            # Получаем количество подписчиков в группе
            if true_group_id < 0:
                true_group_id = -true_group_id
            count_members = session['vk_app'].groups.getMembers(group_id=true_group_id)['count']

            session['count_all_members'] += count_members

            session['list_url'] += \
                f"""<a href="<a href="https://vk.com/public{true_group_id}">https://vk.com/public{true_group_id} - {count_members} подписчиков</a><br />"""

            print(
                f"https://vk.com/public{true_group_id} - {count_members} подписчиков. Всего - {session['count_all_members']}")

            session['count_up'] += 1
            if session['count_up'] > session['count_post_up_max']:
                save_result(session)
                return

            save_result(session)

            time.sleep(random.randint(3, 7))
        except Exception as ext:
            print(ext)
            session['count_down'] += 1
            if str(ext) in "Too many recipients":
                save_result(session)
                return
            session['false_groups_id'].append(true_group_id)
            time.sleep(5)

    return session


def search_new_group(session):
    # Поиск новых групп по ключевым словам региона, если еще остались попытки постов до лимита
    session['list_groups'] = []
    for key in session['rpg_words'].keys():
        new_groups = session['tools'].get_all(method='groups.search', max_count=1000, limit=session['group_count_max'],
                                              values={'q': key, 'type': 'group'})['items']
        session['rpg_words'][key] = len(new_groups)
        session['list_groups'].extend(new_groups)

    session['all_found_groups_from_words'] = 0
    for value in session['rpg_words'].values():
        session['all_found_groups_from_words'] += value

    session['list_groups'] = [dict(t) for t in {tuple(d.items()) for d in session['list_groups']}]

    session['all_found_groups'] = len(session['list_groups'])

    save_result(session)
    shuffle(session['list_groups'])

    return session


def post_in_new_groups(session):
    for group in session['list_groups']:

        # Черный список групп куда постить ненужно
        if group['id'] in session['false_groups_id']:
            session['count_down'] += 1
            continue

        if group['id'] in session['true_groups_id']:
            continue

        if 'can_post' in group and group['can_post'] == 0:
            session['false_groups_id'].append(group['id'])
            session['count_down'] += 1
            continue
        if 'wall' in group and group['wall'] != 1:
            session['false_groups_id'].append(group['id'])
            session['count_down'] += 1
            continue
        try:
            if group['is_closed'] != 0 or group['is_advertiser'] == 1 or 'deactivated' in group:
                session['false_groups_id'].append(group['id'])
                session['count_down'] += 1
                continue
        except Exception as ext:
            session['false_groups_id'].append(group['id'])
            session['count_down'] += 1
            print(f"Непонятная ситуация с ключами, пропускаем группу. Ошибка вот: {ext}")
            continue

        try:
            if group['id'] < 0:
                group['id'] = -group['id']
            members = session['vk_app'].groups.getMembers(group_id=group['id'])
            count_members = members['count']
            if count_members > session['count_members_maximum'] or count_members < session['count_members_minimum']:
                session['false_groups_id'].append(-group['id'])
                session['count_down'] += 1
                continue
        except Exception as ext:
            print(ext)
            session['false_groups_id'].append(group['id'])
            session['count_down'] += 1
            continue

        if group['id'] > 0:
            group['id'] = -group['id']

        try:
            session['vk_app'].wall.post(owner_id=group['id'],
                                        from_group=0,
                                        message=session['reklama_text'],
                                        attachments=session['reklama_attachments'])

            session['count_all_members'] += count_members

            session['list_url'] += \
                f"""<a href="https://vk.com/{group['screen_name']}">https://vk.com/{group['screen_name']} - {count_members} подписчиков</a><br />"""
            print(
                f"{group['screen_name']} - {count_members} подписчиков. Всего - {session['count_all_members']}")
            session['true_groups_id'].append(group['id'])
            session['count_up'] += 1
            if session['count_up'] > session['count_post_up_max']:
                save_result(session)
                return
            if session['count_all_members'] > session['count_members_up_max']:
                save_result(session)
                return

            save_result(session)

            time.sleep(random.randint(3, 7))
        except Exception as ext:
            print(ext)
            session['false_groups_id'].append(group['id'])
            session['count_down'] += 1
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
                return session
            except Exception as exc:
                print(exc)
    return session


if __name__ == '__main__':
    # Подгружаем пользовательские настройки
    sess = global_config.session

    # Ступени работы программы
    sess = get_reklama_post(sess)
    sess = get_sort_groups(sess)
    sess = post_in_sort_groups(sess)
    sess = search_new_group(sess)
    post_in_new_groups(sess)
    print("Работа программы SEO-RPG завершена!")
