# 1. Подключаем инструмент для работы с JSON
import json
import requests
from requests.exceptions import RequestException, HTTPError, Timeout
from bs4 import BeautifulSoup



def get_safe_html(url):
    # 1. Заголовки: обязательны для обхода простых защит
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    try:
        # 2. Запрос с таймаутом (чтобы не висеть вечно)
        response = requests.get(url, headers=headers, timeout=10)

        # 3. Проверка статуса (404, 500 и т.д. вызовут ошибку здесь)
        response.raise_for_status()

        # 4. Исправление кодировки (критично для русских сайтов)
        # detect_encoding анализирует контент и угадывает верную кодировку
        response.encoding = response.apparent_encoding

        return response.text

    except Timeout:
        print(f"❌ Таймаут: Сервер {url} не ответил за 10 сек.")
    except HTTPError as e:
        print(f"❌ Ошибка HTTP {e.response.status_code}: Сервер вернул проблему.")
    except RequestException as e:
        # Сюда попадет всё остальное: нет сети, неверный домен, SSL ошибки
        print(f"❌ Сетевая ошибка: {e}")
    
    # Если была ошибка — возвращаем None, чтобы скрипт не падал дальше
    return None



# === ПРОВЕРКА ===
target_url = "https://pk.mpei.ru/inform/entrants_list.html" # Твой пример

html_content = get_safe_html(target_url)

if html_content:
    # Превращаем набор строк в удобное дерево
    soup = BeautifulSoup(html_content, 'lxml')

    table = soup.find('table', class_='form-grid') # Ищем таблицу с очным бакалавриатом, пока работаем только с ней

    rows = table.find_all('tr') # Разделяем большую таблицу на строки

    for row in rows[1:]: # отдельно обрабатываем каждую строку Кроме первой - там подписи, нам не нужны
        cells = row.find_all('td') # Находим ВСЕ ячейки внутри этой конкретной строки

        if len(cells) == 1: # один столбец = название филиала
            filial = cells[0].get_text() # Вытягиваем название конкретного филиала
            print("\n\n" + "Филиал: " + filial + "\n")


        elif len(cells) == 2: # два столбца = направление + ссылки
            # Здесь в первой ячейке лежит направление, а во второй для какой именно группы + ссылки
            naprav = cells[0].get_text() # Из первой ячейки вытаскиваем название направления

            spisok = cells[1].get_text()
            print(naprav + ": " + spisok + "\n")


        else:
            print(cells) # Что-то странное, надо посмотреть что именно



# if html_content:
#     print(f"✅ Успех! Получено {html_content} символов.")
#     # Тут можно сразу передавать html_content в BeautifulSoup
# else:
#     print("⛔ Данные не получены, парсить нечего.")







# # 2. Создаем данные (словарь Python)
# # Это то, что мы хотим сохранить
# data = {
#     "name": "Иванов И.И.",
#     "score": 250,
#     "agreed": True
# }

# # 3. Открываем файл для ЗАПИСИ
# # "w" = write (создать/перезаписать)
# # encoding="utf-8" = чтобы кириллица не превратилась в \u0418...
# with open("Stepchik_learn_asynk/test.json", "w", encoding="utf-8") as f:
    
#     # 4. Превращаем словарь в JSON и пишем в файл
#     # ensure_ascii=False = оставить русские буквы как есть
#     # indent=2 = красивые отступы (иначе всё в одну строку)
#     json.dump(data, f, ensure_ascii=False, indent=2)

# # 5. Файл автоматически закроется после выхода из with
# print("Готово. Проверь файл test.json в папке со скриптом.")