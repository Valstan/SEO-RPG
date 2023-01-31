#
# Здесь ничего менять нельзя кроме имени файла в конце

from datetime import datetime

import config
from seo_rpg import get_session_vk_api

session = dict()

# Пользовательские настройки (из файла config.py)
session['token'] = config.TOKEN_VK_API
session['login'] = config.LOGIN_VK
session['password'] = config.PASSWORD_VK
session['url_reklama_post'] = config.URL_REKLAMA_POST
session['group_count_max'] = config.group_count_max
session['count_post_up_max'] = config.count_post_up_max
session['count_members_up_max'] = config.count_members_up_max
session['count_members_minimum'] = config.count_members_minimum
session['count_members_maximum'] = config.count_members_maximum

# Выставляем счетчики и накопители (настраивать ненужно)
session['count_up'] = 0
session['count_down'] = 0
session['count_all_members'] = 0
session['list_url'] = ""
session['all_found_groups_from_words'] = 0
session['all_found_groups'] = 0
session['count_false_groups_id'] = 0
session['count_true_groups_id'] = 0

# Разбираем адрес на группу и пост для скачивания.
session['from_group'], session['post_id'] = int(session['url_reklama_post'][19:].split('_'))

# Получаем текущее время, дату для формирования названия файла отчета
session['current_date'] = datetime.now().date()
session['current_time'] = datetime.now().time()

# Подключаемся к API VK
session = get_session_vk_api(session)

# Получаем название рекламируемой группы
session['name_group'] = session['vk_app'].groups.getById(group_ids=-session['from_group'],
                                                         fields='description')['items']['name']

# Название файла отчета (можно изменить)
session['name_file'] = f"Реклама {session['name_group']} от " \
                       f"{str(session['current_date'])}-{str(session['current_time'].hour)}" \
                       f"-{str(session['current_time'].minute)}.html"
