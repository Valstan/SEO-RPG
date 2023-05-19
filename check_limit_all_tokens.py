from bin.check_one_token_limit import check_one_token_limit
from bin.load_base_tokens import load_base_tokens


def check_limit_all_tokens(session):
    all_limit = 0

    for key, value in session['tokens_shuts'].items():
        limit = check_one_token_limit(value)
        print(f"У токена - {key} - осталось {limit} попыток.")
        all_limit += limit

    return all_limit


if __name__ == '__main__':
    sess = {}
    sess = load_base_tokens(sess)
    print(f"Всего осталось - {check_limit_all_tokens(sess)} попыток.")
