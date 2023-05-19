import json
import os

import config
from bin.get_reklama_post import get_reklama_post
from bin.get_session import get_session
from bin.get_sort_groups import get_sort_groups
from bin.post_in_sort_groups import post_in_sort_groups
from check_limit_all_tokens import check_limit_all_tokens

# Сверим аппетиты рекламщика и возможности токенов

session = get_session()
print(f"Токенов осталось на {check_limit_all_tokens(session)} раз, а реклам заказал на {config.count_post_up_max} раз.")
session = get_reklama_post(session)
if not session:
    print("Я не нашел нужный пост, где-то ошибка, или он далеко ушел по ленте.")
    quit()
session = get_sort_groups(session)
session = post_in_sort_groups(session)

# Сохраняем базу меток использования токенов
with open(os.path.join("base/tokens_shuts.json"), 'w', encoding='utf-8') as f:
    f.write(json.dumps(session['tokens_shuts'], indent=2, ensure_ascii=False))

# Сохраняем список ID программно выявленных плохих групп
with open(os.path.join("base/update_black_ids.json"), 'w', encoding='utf-8') as f:
    f.write(json.dumps(session['update_black_ids'], indent=2, ensure_ascii=False))

print("Работа программы SEO-RPG завершена!")
