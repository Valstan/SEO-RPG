import json
import os
import time

from vk_api import VkApi, VkTools

import config

# Выставляем счетчики и накопители (настраивать ненужно)
count_up = 0
count_down = 0
count_all_members = 0

# Название файла базы
name_file_base_id = f"base/{config.keyword}_база_id.json"

# Загружаем свой черный список групп, которые нафик не нужны
try:
    with open(os.path.join(f"base/main_black_ids.json"), 'r', encoding='utf-8') as f:
        black_ids = json.load(f)
except:
    print(f"Нет файла черного списка - base/main_black_ids.json")
    quit()

# Подключаемся к ВК
vk_session = VkApi(token=config.TOKEN_VK_API_1)
vk_app = vk_session.get_api()
vk_tools = VkTools(vk_session)

# Поиск новых групп по ключевым словам региона, если еще остались попытки постов до лимита
list_groups = vk_tools.get_all(method='groups.search', max_count=1000,
                               values={'q': config.keyword, 'type': 'group'})['items']
time.sleep(0.3)

base_id = []
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
            live_members_ping = vk_app.groups.getMembers(group_id=abs(group['id']), offset=offset, fields='city')
        except:
            offset = 10000000000
            break
        if live_members_ping['count'] < 300:
            offset = 10000000000
            break
        live_members += live_members_ping['items']
        if offset > live_members_ping['count'] or live_members_ping['count'] < 1000:
            break
        offset += 1000

    if offset == 10000000000:
        count_down += 1
        continue

    members = []
    for i in live_members:
        if 'deactivated' not in i:
            members.append(i['id'])

    base_id.append([group['id'], len(members), members])
    count_all_members += len(members)

    count_up += 1
    print(f"Всего - {all_found_groups}. Готово - {int((count_up + count_down) / (all_found_groups / 100))}%."
          f" Хорошие - {count_up}. Отказ - {count_down}. Подписота - {len(members)}. Вся подписота - {count_all_members}.")

# Сохраняем работу в файл
with open(os.path.join(name_file_base_id), 'w',
          encoding='utf-8') as f:
    f.write(json.dumps(base_id, indent=2, ensure_ascii=False))

# Подсчитываем количество уникальных подписчиков
unique_members = []
for i in base_id:
    unique_members += i[2]
unique_members = len(list(set(unique_members)))

# Выводим итоговый отчет в консоль
print(f"{config.keyword} - Всего - {all_found_groups}. Хорошие - {count_up}. Отказ - {count_down}."
      f" Вся живая подписота - {count_all_members}. Уникальные - {unique_members}")

print(f"Обновление базы данных групп по поисковому запросу '{config.keyword}', завершена!")
