import json
import os
import random
import time

import config
from bin.get_session_vk_api import get_session_vk_api
from bin.load_base_tokens import load_base_tokens
from bin.load_bases import load_bases

# Загружаем базы белых и черных списков ID
base_ids, main_black_ids, update_black_ids = load_bases()
black_ids = main_black_ids + update_black_ids

# Готовим список ключевых слов
list_key_words = config.keywords.split(",")
session = {}

# Загружаем базу токенов
session = load_base_tokens(session)

for keyword in list_key_words:

    # Создаем (или очищаем) базу ID для ключевого слова
    base_ids[keyword] = []

    # Выставляем счетчики и накопители (настраивать ненужно)
    count_up = 0
    count_down = 0
    count_all_members = 0

    # Выбираем имя токена для соединения с ВК
    session['name_work_token'] = random.choice(session['karusel_tokens'])

    # Подсоединяемся к ВК
    session = get_session_vk_api(session, vkapp=True, vktools=True)

    print(f"Слово - {keyword}. Токен - {session['name_work_token']}")

    # Поиск новых групп по ключевым словам региона
    list_groups = session['tools'].get_all(method='groups.search', max_count=1000,
                                           values={'q': keyword, 'type': 'group'})['items']
    time.sleep(0.3)

    all_found_groups = len(list_groups)

    for group in list_groups:
        if abs(group['id']) in black_ids:
            count_down += 1
            continue
        if 'can_post' in group and group['can_post'] == 0:
            count_down += 1
            continue
        if 'wall' in group and group['wall'] != 1:
            count_down += 1
            continue
        try:
            if group['is_closed'] != 0 or group['is_advertiser'] == 1 or 'deactivated' in group:
                count_down += 1
                continue
        except:
            count_down += 1
            continue

        live_members = []
        offset = 0
        while True:
            time.sleep(0.3)
            try:
                live_members_ping = session['vk_app'].groups.getMembers(group_id=abs(group['id']), offset=offset, fields='city')
            except:
                offset = False  # Подписчиков не дает, группу в баню
                break
            if live_members_ping['count'] < config.count_minimum_members:
                offset = False  # мало подписчиков группу в баню
                break
            live_members += live_members_ping['items']
            if offset > live_members_ping['count'] or live_members_ping['count'] < 1000:
                offset = True  # все нормально, подписчиков набрал
                break
            offset += 1000

        if not offset:
            count_down += 1
            continue

        members = []
        for i in live_members:
            if ('deactivated' or 'banned') not in i:
                members.append(i['id'])

        base_ids[keyword].append([group['id'], len(members), members])
        count_all_members += len(members)

        count_up += 1
        print(f"Всего - {all_found_groups}. Готово - {int((count_up + count_down) / (all_found_groups / 100))}%."
              f" Хорошие: {count_up}. Отказ: {count_down}. Подписота: {len(members)}. Все: {count_all_members}.")

    # Подсчитываем количество уникальных подписчиков
    unique_members = []
    for i in base_ids[keyword]:
        unique_members += i[2]
    unique_members = len(list(set(unique_members)))

    # Выводим итоговый отчет в консоль
    print(f"{keyword} - Всего - {all_found_groups}. Хорошие - {count_up}. Отказ - {count_down}."
          f" Вся живая подписота - {count_all_members}. Уникальные - {unique_members}")

    print(f"Обновление базы данных групп по поисковому запросу '{keyword}', завершена!")


# Сохраняем базу ID групп по ключевым словам поиска
with open(os.path.join("base/base_ids_by_keywords.json"), 'w', encoding='utf-8') as f:
    f.write(json.dumps(base_ids, indent=2, ensure_ascii=False))
