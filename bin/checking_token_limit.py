import json
import os
from datetime import datetime

import config
from bin.get_session_vk_api import get_session_vk_api


def checking_token_limit(session):
    while True:
        if not session['shut_token']:
            session['token'] = session['tokens'][0][1]

            try:
                with open(os.path.join(f"base/{session['tokens'][0][0]}_shut_token.json"), 'r', encoding='utf-8') as f:
                    session['shut_token'] = json.load(f)
            except:
                session['shut_token'] = [1643164102]  # Старая дата где-то из 2022 года
                with open(os.path.join(f"base/{session['tokens'][0][0]}_shut_token.json"), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(session['shut_token'], indent=2, ensure_ascii=False))
            # Подключаемся к API VK
            session = get_session_vk_api(session)

        limit = config.token_limit + 1
        curr_dt = datetime.now()
        time_day_ago = int(round(curr_dt.timestamp())) - 90000
        for i in session['shut_token']:
            if i > time_day_ago:
                limit -= 1

        if limit < 0:
            with open(os.path.join(f"base/{session['tokens'][0][0]}_shut_token.json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(session['shut_token'], indent=2, ensure_ascii=False))
            session['shut_token'] = []
            del session['tokens'][0]
            if not session['tokens']:
                print("!!! У всех токенов закончился лимит на публикации.")
                return session
            else:
                continue
        else:
            return session
