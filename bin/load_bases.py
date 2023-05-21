import json
import os


# Параметр all_ok означает, что в случае отсутствия файла,
# программа не спрашивая пользователя создаст и вернет по return пустые базы

def load_bases(all_ok=False):
    # Загружаем базу ID групп по словам поиска
    base_ids = {}
    try:
        with open(os.path.join(f"base/base_ids_by_keywords.json"), 'r', encoding='utf-8') as f:
            base_ids = json.load(f)
    except:
        if not all_ok:
            if input(f"Нет файла базы ID групп - base/base_ids_by_keywords.json\n"
                     f"Продолжить работу - Enter\n"
                     f"Выйти из программы и найти этот файл - 0") == '0':
                quit()

    # Загружаем свой черный список групп, которые нафик не нужны
    main_black_ids = []
    try:
        with open(os.path.join(f"base/main_black_ids.json"), 'r', encoding='utf-8') as f:
            main_black_ids = json.load(f)
    except:
        if not all_ok:
            if input(f"Нет файла РУЧНОГО черного списка - base/main_black_ids.json\n"
                     f"Продолжить работу - Enter\n"
                     f"Выйти из программы и найти этот файл - 0") == '0':
                quit()

    # Загружаем программный черный список групп, которые не дают размещать объявления
    update_black_ids = []
    try:
        with open(os.path.join(f"base/update_black_ids.json"), 'r', encoding='utf-8') as f:
            update_black_ids = json.load(f)
    except:
        if not all_ok:
            if input(f"Нет файла ПРОГРАММНОГО черного списка - base/update_black_ids.json\n"
                     f"Продолжить работу - Enter\n"
                     f"Выйти из программы и найти этот файл - 0") == '0':
                quit()

    return base_ids, main_black_ids, update_black_ids
