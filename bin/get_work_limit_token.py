import random

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
            session = get_session_vk_api(session)
            return session, 10
        elif work_limit_token:
            session = get_session_vk_api(session)
            return session, work_limit_token
        else:
            pass

    return session, 0
