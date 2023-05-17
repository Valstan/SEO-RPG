import json
import os

import config
from bin.checking_token_limit import checking_token_limit
from bin.get_reklama_post import get_reklama_post
from bin.get_session import get_session
from bin.get_sort_groups import get_sort_groups
from bin.karusel_tokens import karusel_tokens
from bin.post_in_sort_groups import post_in_sort_groups
from check_token_limit import count_limit_tokens

# Сверим аппетиты рекламщика и возможности токенов
last_limit_token = count_limit_tokens(config.token_limit)
print(f"Токенов осталось на {last_limit_token} раз, а реклам заказал на {config.count_post_up_max} раз. ")
session = karusel_tokens()
session['shut_token'] = []
session = checking_token_limit(session)
session = get_session(session)
session = get_reklama_post(session)
session = get_sort_groups(session)
session = post_in_sort_groups(session)



with open(os.path.join("base/update_black_ids.json"), 'w', encoding='utf-8') as f:
    f.write(json.dumps(session['update_black_ids'], indent=2, ensure_ascii=False))


print("Работа программы SEO-RPG завершена!")
