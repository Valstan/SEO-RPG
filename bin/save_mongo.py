def save_mongo(session):

    # Сохраняем базу меток использования токенов
    with open(os.path.join("base/tokens_shuts.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(session['tokens_shuts'], indent=2, ensure_ascii=False))

    # Сохраняем список ID программно выявленных плохих групп
    with open(os.path.join("base/update_black_ids.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(session['update_black_ids'], indent=2, ensure_ascii=False))
