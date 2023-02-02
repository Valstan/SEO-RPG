import json
import os
from datetime import datetime

import config


def check_token_limit(name_token):
    with open(os.path.join(f"{name_token}_shut_token.json"), 'r', encoding='utf-8') as f:
        shut_token = json.load(f)

    limit = 80
    curr_dt = datetime.now()
    time_day_ago = int(round(curr_dt.timestamp())) - 90000
    for i in shut_token:
        if i > time_day_ago:
            limit -= 1

    print(f"У токена - {name_token} - осталось {limit} попыток.")


if __name__ == '__main__':
    if config.TOKEN_VK_API_1_name:
        check_token_limit(config.TOKEN_VK_API_1_name)
    if config.TOKEN_VK_API_2_name:
        check_token_limit(config.TOKEN_VK_API_2_name)
    if config.TOKEN_VK_API_3_name:
        check_token_limit(config.TOKEN_VK_API_3_name)
    if config.TOKEN_VK_API_4_name:
        check_token_limit(config.TOKEN_VK_API_4_name)
    if config.TOKEN_VK_API_5_name:
        check_token_limit(config.TOKEN_VK_API_5_name)
