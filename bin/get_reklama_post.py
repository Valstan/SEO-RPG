import re

import config
from bin.get_attach import get_attach


def get_reklama_post(session):
    # Получаем пост, который будем рекламировать.
    reklama_posts = session['vk_app'].wall.get(owner_id=session['from_group'], count=100, offset=0)['items']

    # Находим нужный нам пост по его ID
    for sample in reklama_posts:
        if sample['id'] == session['post_id']:

            # Забираем картинки
            session['reklama_attachments'] = get_attach(sample)

            # Если нужна подпись под текстом, добавляем её
            if config.url_reklama:
                sample[
                    'text'] = f"{sample['text']}\n\n{config.signature_after} @https://vk.com/public{abs(session['from_group'])} (\"{session['name_group']}\") {config.signature_before}."

            # Берем первый чистый текст в список текстов
            session['list_reklama_text'].append(sample['text'])

            # Набираем следующие тексты с измененными буквами на латиницу
            for i in range(0, len(config.letter_sub[0]) - 1):
                session['list_reklama_text'].append(
                    f"{re.sub(config.letter_sub[0][i], config.letter_sub[1][i], sample['text'], 0, re.M)}")

            return session
