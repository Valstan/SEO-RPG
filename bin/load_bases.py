from bin.get_mongo import table


def load_bases():

    # Загружаем базу ID групп по словам поиска
    base_ids = table['base_ids']

    # Загружаем свой черный список групп, которые нафик не нужны
    main_black_ids = table['main_black_ids']

    # Загружаем программный черный список групп, которые не дают размещать объявления
    update_black_ids = table['update_black_ids']

    return base_ids, main_black_ids, update_black_ids
