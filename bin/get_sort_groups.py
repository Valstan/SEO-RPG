import json
import os
import random

import config


def get_sort_groups(session):
    session['base'] = []
    base = []
    dubl_group = []
    unique_members = []

    for keyword in session['list_key_words']:
        if keyword not in session['base_ids']:
            print(f"По ключевому слову поиска - '{keyword}'"
                  f" нет базы данных ID групп, сначала создай ее скриптом update_groups_base_by_keys.py")
            quit()
        base += session['base_ids'][keyword]

    # Перемешиваем список ID или наоборот сортируем от самой большой группы к маленькой
    if config.group_shuffle:
        random.shuffle(base)
    else:
        # base = sorted(base, key=lambda item: item[1], reverse=True)
        base.sort(key=lambda x: x[1], reverse=True)

    for group in base:

        true_group_id = abs(int(group[0]))
        if true_group_id in dubl_group:
            continue
        dubl_group.append(true_group_id)

        if group[1] < config.count_members_minimum:
            continue

        if true_group_id in session['main_black_ids'] or true_group_id in session['update_black_ids']:
            continue

        unique_members = list(set(unique_members + group[2]))

        session['base'] += [group]

    session['all_found_groups'] = len(session['base'])
    session['all_found_members'] = len(unique_members)

    return session
