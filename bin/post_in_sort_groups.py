import json
import os
import random
import time
from datetime import datetime

from bin.checking_token_limit import checking_token_limit
from bin.save_result import save_result


def post_in_sort_groups(session):
    unique_members = []
    dubl_group = []

    for group in session['base']:

        true_group_id = abs(int(group[0]))
        if true_group_id in dubl_group:
            continue
        dubl_group.append(true_group_id)

        if true_group_id in session['main_black_ids'] or true_group_id in session['update_black_ids']:
            session['count_down'] += 1
            continue

        session = checking_token_limit(session)
        if not session['tokens']:
            print("Кончились токены, сорян...")
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

        except Exception as ext:
            if "Too many recipients" in str(ext):
                print(ext)
                break
            if "user should be group editor" in str(ext) or "Access denied" in str(ext):
                session['update_black_ids'].append(true_group_id)
            session['count_down'] += 1

        print(f"https://vk.com/public{true_group_id} - {group[1]} подписчиков. Всего - {session['count_all_members']}")
        save_result(session)
        curr_dt = datetime.now()
        session['shut_token'].append(int(round(curr_dt.timestamp())))
        if len(session['shut_token']) > 100:
            del session['shut_token'][0]

        if session['count_up'] > session['count_post_up_max'] or \
                session['count_all_members'] > session['count_members_up_max']:
            save_result(session)
            break

        time.sleep(random.randint(2, 7))
