# Нужно True или нет False перемешивать буквы в сообщениях
letter_sub = False

# Адрес готового рекламного поста, который будем рекламировать
# Адрес должен выглядеть так: "https://vk.com/wall-168247378_787"
URL_REKLAMA_POST = "https://vk.com/wall-218688001_1530"  # Адрес поста вписать между кавычек

# Ключевые слова через запятую, для региона поиска новых групп
# Рядом с запятой ПРОБЕЛЫ СТАВИТЬ НЕЛЬЗЯ, в названиях городов ПРОБЕЛЫ СТАВИТЬ МОЖНО
# регистр букв не имеет значения, проще использовать маленькие буквы
# Пример заполнения:
# KEY_WORDS = "малмыж,кильмезь,вятские поляны,уржум,кукмор,балтаси,киров"
KEY_WORDS = "малмыж,кильмезь,вятские поляны,уржум,кукмор,балтаси"  # Слова вписать между кавычек

# Нужна или нет подпись в тексте с рекламной ссылкой на группу
url_reklama = True  # True - ДА добавить подпись, False - НЕТ не надо добавлять подпись
signature_after = "Еще больше интересного в "  # Текст до ссылки на группу
signature_before = "!"  # Текст после ссылки на группу

# Перемешать все группы (True) или размещать с самых больших (False)
group_shuffle = False

# Сколько нужно сделать публикаций.
# Зависит от количества лимита на токен и количества токенов, далее программа сама остановится
count_post_up_max = 500

# Минимум подписчиков в группе для разрешения публикации
# Например, если укажете 2000, то публиковать в группах в которых подписчиков меньше 2000 не будем
count_members_minimum = 0

# Максимум подписчиков в группе для разрешения публикации
# Здесь наоборот, если подписчиков в группе больше чем вы тут укажете, то пост в них публиковаться не будет
# Если верхняя граница подписчиков не нужна, то укажите здесь 0
count_members_maximum = 0

# Максимальное количество подписчиков во всех группах вместе, где разместится рекламный пост,
# после набора количества которых завершаем работу программы
# Варианты - 100000 или 200000 или 0 если остановка программы будет по количеству опубликованных постов
count_members_up_max = 0

# Список слов для скрипта обновления баз ID групп по ключевым словам поиска
keywords = "киров"
# Минимальное количество подписчиков в найденной группе (из них потом удалится еще куча собачек)
count_minimum_members = 400

# Лимит ВК на рекламные сообщения в сутки на один токен
# Последний лимит знаю что на 80 сообщений в сутки был
token_limit = 80
