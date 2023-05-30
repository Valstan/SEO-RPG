import random
import time

from bin.check_one_token_limit import check_one_token_limit
from bin.get_session_vk_api import get_session_vk_api


def get_work_limit_token(session):

    for i in range(100):

        # Принудительная смена токена
        # Запоминаем имя текущего токена
        last_name_work_token = session['name_work_token']

        # Выбираем новое имя до тех пор, пока оно не сменится
        while True:
            session['name_work_token'] = random.choice(session['karusel_tokens'])
            if last_name_work_token != session['name_work_token']:
                break

        # Проверяем оставшееся число попыток у нового токена
        work_limit_token = check_one_token_limit(session['tokens_shuts'][session['name_work_token']])
        print(f"Сменил токен на {session['name_work_token']} - у него {work_limit_token} попыток")
        if work_limit_token and work_limit_token > 10:
            try:
                session = get_session_vk_api(session, vkapp=True)
                return session, 10
            except:
                time.sleep(1)
                continue

        elif work_limit_token:
            try:
                session = get_session_vk_api(session, vkapp=True)
                return session, work_limit_token
            except:
                time.sleep(1)
                continue
        else:
            pass

    print("Все токены исчерпали свои попытки на сегодня!")
    return session, 0
