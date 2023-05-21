import json
import os

try:
    with open(os.path.join("base/main_black_ids.json"), 'r', encoding='utf-8') as f:
        main_black_ids = json.load(f)
except:
    main_black_ids = [0]

while True:

    black_id = (abs(int(input("Введите ID группы для занесения в черный список: "))))
    if not black_id:
        break
    if black_id in main_black_ids:
        print("Данный ID уже есть в базе данных запрещенных ID")
    else:
        main_black_ids.append(black_id)
        with open(os.path.join("base/main_black_ids.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(main_black_ids, indent=2, ensure_ascii=False))
