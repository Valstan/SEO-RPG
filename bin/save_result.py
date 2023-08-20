import os

import config


def save_result(session):
    print(f"Опубликовано - {session['count_up']}. Пропущено - {session['count_down']}. "
          f"Обработал {session['count_up'] + session['count_down']} из {session['all_found_groups']}.")

    result = r"<html><head><style>" \
             r"body{background-color:#339966;}h3{background-color:#00b33c;}p{background-color:#FFFFFF);}" + \
             f"""</style><title>{session['data_work']} {session['text_post'][:15]}</title></head><body>
<h2>{session['name_group']}. {session['data_work']}. <a href="{config.URL_REKLAMA_POST}">{config.URL_REKLAMA_POST}</a></h2>
<h3>Текст поста: "{session['text_post']}"<br />
Список ключевых слов поиска: {str(session['list_key_words'])}<br />
Подпись-ссылка в группу: {config.url_reklama}. Сделать {config.count_post_up_max} размещений.<br />
Диапазон подписчиков: Мин: {config.count_members_minimum}, Макс: {config.count_members_maximum}, Всего: {session['count_members_up_max']}<br />
Найдено групп: {session['all_found_groups']} с {session['all_found_members']} уникальными подписчиками.</h3>
<h2>Обработано: {session['count_up'] + session['count_down']}, Бан: {session['count_down']}<br />
Успешных объявлений {session['count_up']} - {session['count_all_members']} уникальных подписчиков.<h2>
<h3>Список ссылок на группы в которых удалось разместить объявление:</h3>
<h3>{session['list_url']}</h3><br /> <br /> <br /> <br /></body></html>"""

    if session['manual']:
        with open(os.path.join(session['name_file']), 'w', encoding='utf-8') as f:
            f.write(result)
