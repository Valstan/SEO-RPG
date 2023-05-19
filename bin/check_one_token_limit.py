from datetime import datetime

import config


def check_one_token_limit(shuts_token):
    limit = config.token_limit
    curr_dt = datetime.now()
    time_day_ago = int(round(curr_dt.timestamp())) - 86500

    for shut in shuts_token:
        if shut > time_day_ago:
            limit -= 1

    return limit
