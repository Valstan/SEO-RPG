import json
import os
from datetime import datetime

import config


def check_token_limit(name_token, lim=60):
    with open(os.path.join(f"base/{name_token}_shut_token.json"), 'r', encoding='utf-8') as f:
        shut_token = json.load(f)

    curr_dt = datetime.now()
    time_day_ago = int(round(curr_dt.timestamp())) - 90000
    for i in shut_token:
        if i > time_day_ago:
            lim -= 1

    print(f"У токена - {name_token} - осталось {lim} попыток.")

    return lim


def count_limit_tokens(limit=60):
    all_limit = 0
    if config.TOKEN_VK_API_1_name:
        all_limit += check_token_limit(config.TOKEN_VK_API_1_name, limit)
    if config.TOKEN_VK_API_2_name:
        all_limit += check_token_limit(config.TOKEN_VK_API_2_name, limit)
    if config.TOKEN_VK_API_3_name:
        all_limit += check_token_limit(config.TOKEN_VK_API_3_name, limit)
    if config.TOKEN_VK_API_4_name:
        all_limit += check_token_limit(config.TOKEN_VK_API_4_name, limit)
    if config.TOKEN_VK_API_5_name:
        all_limit += check_token_limit(config.TOKEN_VK_API_5_name, limit)
    return all_limit


if __name__ == '__main__':
    print(count_limit_tokens())
