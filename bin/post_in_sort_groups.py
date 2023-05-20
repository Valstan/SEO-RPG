import random
import time
from datetime import datetime

import config
from bin.get_work_limit_token import get_work_limit_token
from bin.save_result import save_result


def post_in_sort_groups(session):
    unique_members = []
    dubl_group = []
    count_shuts_token = 0

    for group in session['base']:

        true_group_id = abs(int(group[0]))
        if true_group_id in dubl_group:
            continue
        dubl_group.append(true_group_id)

        if group[1] < config.count_members_minimum:
            continue

        if true_group_id in session['main_black_ids'] or true_group_id in session['update_black_ids']:
            continue

        if count_shuts_token < 1:
            session, count_shuts_token = get_work_limit_token(session)
            if count_shuts_token < 1:
                break

        session['count_rek_posts'] += 1
        if session['count_rek_posts'] == len(session['list_reklama_text']):
            session['count_rek_posts'] = 0

        try:
            session['vk_app'].wall.post(owner_id=-true_group_id,
                                        from_group=0,
                                        message=session['list_reklama_text'][session['count_rek_posts']],
                                        attachments=session['reklama_attachments'])

            unique_members = list(set(unique_members + group[2]))
            session['count_all_members'] = len(unique_members)

            session['list_url'] += \
                f"""<a href="https://vk.com/public{true_group_id}">https://vk.com/public{true_group_id} - {group[1]} подписчиков</a><br />"""

            session['count_up'] += 1

            print(f"Разместил в {true_group_id} - {group[1]} подписчиков. Всего - {session['count_all_members']}")

        except Exception as ext:
            if "Too many recipients" in str(ext):
                print(ext)
                break
            print(f"Ошибка - {ext}. Забанил {true_group_id} - {group[1]} подписоты.")
            session['update_black_ids'].append(true_group_id)
            session['count_down'] += 1

        save_result(session)

        curr_dt = datetime.now()
        if session['name_work_token'] not in session['tokens_shuts']:
            session['tokens_shuts'][session['name_work_token']] = []
        session['tokens_shuts'][session['name_work_token']].append(int(round(curr_dt.timestamp())))
        if len(session['tokens_shuts'][session['name_work_token']]) > 100:
            del session['tokens_shuts'][session['name_work_token']][0]
        count_shuts_token -= 1

        if session['count_up'] > config.count_post_up_max or \
                session['count_all_members'] > session['count_members_up_max']:
            save_result(session)
            break

        time.sleep(random.randint(2, 7))

    return session
