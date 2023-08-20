from bin.get_mongo import table


def load_base_tokens(session):
    # Загружаем базу токенов с попытками
    session['tokens_shuts'] = table['tokens_shuts']
    session['tokens'] = {}
    session['karusel_tokens'] = []
    priority = 1
    table['TOKENS'].reverse()
    for token_one in table['TOKENS']:
        priority *= 2
        for i in range(priority):
            session['karusel_tokens'].append(token_one[0])

        session['tokens'][token_one[0]] = token_one[1]

    return session
