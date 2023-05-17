import os

import config


def save_result(session):
    print(f"Опубликовано - {session['count_up']}. Пропущено - {session['count_down']}. "
          f"Обработал {session['count_up'] + session['count_down']} из {session['all_found_groups']}.")

    result = f"""<html>
            <head>
            <title>Title</title>
            </head>
            <body>
            <h2>Кого или что рекламируем: {config.name_reklama}</h2>
            <h2>Адрес рекламируемого поста: <a href="{config.URL_REKLAMA_POST}">{config.URL_REKLAMA_POST}</a></h2>
            Список ключевых слов поиска:<br />
            {session['list_key_words']}<br />
            Подпись-ссылка в группу: {config.url_reklama}. Сделать {config.count_post_up_max} размещений.<br />
            Диапазон количества подписчиков в группе:<br />
            Мин - {config.count_members_minimum}, Макс - {config.count_members_maximum}, Всего - {config.count_members_up_max}<br />
            <h2>Всего найдено: {session['all_found_groups']} групп.<br />
            Обработано {session['count_up'] + session['count_down']} групп<br />
            Успешно размещено {session['count_up']} объявлений для {session['count_all_members']} уникальных подписчиков.<br />
            {session['count_down']} групп отсеяно за негодностью.<br />
            <h2>Список ссылок на группы в которых удалось разместить объявление:</h2>
            <p>{session['list_url']}</p>
            <br /> <br /> <br /> <br />       
            </body>
            </html>
            """

    with open(os.path.join(session['name_file']), 'w', encoding='utf-8') as f:
        f.write(result)
