import config


def karusel_tokens():
    session = dict()
    session['tokens'] = []
    # Собираем карусель токенов
    if config.TOKEN_VK_API_1:
        session['tokens'].append([config.TOKEN_VK_API_1_name, config.TOKEN_VK_API_1])
    if config.TOKEN_VK_API_2:
        session['tokens'].append([config.TOKEN_VK_API_2_name, config.TOKEN_VK_API_2])
    if config.TOKEN_VK_API_3:
        session['tokens'].append([config.TOKEN_VK_API_3_name, config.TOKEN_VK_API_3])
    if config.TOKEN_VK_API_4:
        session['tokens'].append([config.TOKEN_VK_API_4_name, config.TOKEN_VK_API_4])
    if config.TOKEN_VK_API_5:
        session['tokens'].append([config.TOKEN_VK_API_5_name, config.TOKEN_VK_API_5])
    return session
