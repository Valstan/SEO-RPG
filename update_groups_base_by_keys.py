import json
import os
import random
import time

from vk_api import VkApi, VkTools

import config

# Выставляем счетчики и накопители (настраивать ненужно)
count_up = 0
count_down = 0
count_all_members = 0

# Название файла базы
name_file_base_id = f"base/{config.keyword}_база_id.json"

# Подключаемся к ВК
vk_session = VkApi(token=config.TOKEN_VK_API_1)
vk_app = vk_session.get_api()
vk_tools = VkTools(vk_session)

# Поиск новых групп по ключевым словам региона, если еще остались попытки постов до лимита
list_groups = vk_tools.get_all(method='groups.search', max_count=1000, limit=1000,
                               values={'q': config.keyword, 'type': 'group'})['items']

base_id = {}
all_found_groups = len(list_groups)

for group in list_groups:

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

    try:
        members = vk_app.groups.getMembers(group_id=abs(group['id']))['count']
        count_all_members += members
        base_id[str(group['id'])] = members

        with open(os.path.join(name_file_base_id), 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(base_id, indent=2, ensure_ascii=False))

        count_up += 1
        print(f"Всего - {all_found_groups}. Готово - {int((count_up + count_down)/(all_found_groups / 100))}%."
              f" Осталось - {all_found_groups - count_up - count_down}."
              f" Хорошие - {count_up}. Отказ - {count_down}. Подписоты - {count_all_members}")

    except:
        count_down += 1

    time.sleep(random.randint(2, 4))

print(f"Обновление базы данных групп по поисковому запросу '{config.keyword}', завершена!")
