import re

import config
from bin.get_attach import get_attach
from bin.get_mongo import table


def get_reklama_post(session):
    # Получаем пост, который будем рекламировать.
    reklama_posts = session['vk_app'].wall.get(owner_id=session['from_group'], count=100, offset=0)['items']

    # Находим нужный нам пост по его ID
    for sample in reklama_posts:
        if sample['id'] == session['post_id']:

            # Забираем текст поста для отчета
            session['text_post'] = sample['text'][:100]

            # Забираем картинки
            session['reklama_attachments'] = get_attach(sample)

            # Если нужна подпись под текстом, добавляем её
            if config.url_reklama:
                sample[
                    'text'] = f"{sample['text']}\n\n{config.signature_after} @https://vk.com/public{abs(session['from_group'])} (\"{session['name_group']}\") {config.signature_before}."

            # Забираем один чистый текст
            session['list_reklama_text'].append(sample['text'])

            # Если ручной запуск и если надо, то набираем следующие тексты с измененными буквами на латиницу
            if session['manual'] and config.letter_sub:
                session['letter_sub'] = table['letter_sub']
                count_post = 0
                for i in range(len(session['letter_sub'][0])):
                    session['list_reklama_text'].append(
                        f"{re.sub(session['letter_sub'][0][i], session['letter_sub'][1][i], sample['text'], 0, re.M)}")
                    count_post += 1
                    if count_post > config.count_post_up_max:
                        return session
                for count in range(len(session['letter_sub'][0])):
                    texts = session['list_reklama_text']
                    session['letter_sub'][0].append(session['letter_sub'][0][0])
                    del session['letter_sub'][0][0]
                    session['letter_sub'][1].append(session['letter_sub'][1][0])
                    del session['letter_sub'][1][0]
                    for i in range(len(session['letter_sub'][0])):
                        for text in texts:
                            session['list_reklama_text'].append(
                                f"{re.sub(session['letter_sub'][0][i], session['letter_sub'][1][i], text, 0, re.M)}")
                            count_post += 1
                            if count_post > config.count_post_up_max:
                                return session

            return session
