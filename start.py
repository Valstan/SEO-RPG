from sys import argv

import config
from bin.get_mongo import table
from bin.get_reklama_post import get_reklama_post
from bin.get_session import get_session
from bin.get_sort_groups import get_sort_groups
from bin.post_in_sort_groups import post_in_sort_groups
from bin.save_mongo import save_mongo
from check_limit_all_tokens import check_limit_all_tokens

session = dict()

# Имя аккаунта владельца токена и сам токен аккаунта Вконтакте (пишутся внутри кавычек)
session['TOKENS'] = table['TOKENS']
# Токен доступа к вашему Яндекс-диску (если есть) для сохранения работы программы на Яндекс-Диск
YANDEX_DISK_TOKEN = table['YANDEX_DISK_TOKEN']

if len(argv) == 2:
    # Включаем автоматический режим. Скрипт работает на сервере.
    session['server'] = True
    session = get_session(session)
    # Отключаем перемешивание букв в текстах
    session['letter_sub'] = False
    pass
else:
    print(
        f"Токенов осталось на {check_limit_all_tokens(session)} раз, а реклам заказал на {config.count_post_up_max} раз.")
    session = get_reklama_post(session)
    if not session:
        print("Я не нашел нужный пост, где-то ошибка, или он далеко ушел по ленте.")
        quit()


session = get_sort_groups(session)
session = post_in_sort_groups(session)

# Сохраняем статистику скрипта в базу Монго
save_mongo(session)


if session['manual']:
    print("Работа программы SEO-RPG завершена!")
