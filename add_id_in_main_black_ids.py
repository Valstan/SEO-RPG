import json
import os

try:
    with open(os.path.join("base/main_black_ids.json"), 'r', encoding='utf-8') as f:
        main_black_ids = json.load(f)
except:
    main_black_ids = [0]

while True:

    str_black_id = input("Введите ID группы для занесения в черный список: ")

    if not str_black_id:
        quit()

    if 'wall' in str_black_id:
        text_list = str_black_id.split(sep="wall")
        text_list = text_list[1].split(sep="_")
        black_id = abs(int(text_list[0]))
    else:
        black_id = abs(int(str_black_id))

    print(black_id)

    if black_id in main_black_ids:
        print("Данный ID уже есть в базе данных запрещенных ID")
    else:
        main_black_ids.append(black_id)
        with open(os.path.join("base/main_black_ids.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(main_black_ids, indent=2, ensure_ascii=False))
        print("Группа добавлена в баню.")
