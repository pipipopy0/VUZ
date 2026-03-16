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

    data = {} # Пустой словарь, который заполниться и пойдет в json

    filial = "НИУ «МЭИ» г. Москва" # Сначала по умолчанию идет основной вуз который в москве
    data[filial] = {}

    for row in rows[1:]: # отдельно обрабатываем каждую строку Кроме первой - там подписи, нам не нужны
        cells = row.find_all('td') # Находим ВСЕ ячейки внутри этой конкретной строки

        if len(cells) == 1: # один столбец = название филиала
            filial = cells[0].get_text() # Вытягиваем название конкретного филиала
            data[filial] = {}
            

        elif len(cells) == 2: # два столбца = направление + ссылки
            # Здесь в первой ячейке лежит направление, а во второй для какой именно группы + ссылки

            naprav = cells[0].get_text() # Из первой ячейки вытаскиваем название направления
            groups = cells[1].find_all('a') # Из второй ячейки вытаскиваем массив ссылок с названиями групп

            data[filial][naprav] = {}

            one_naprav = {} # Массив для того, чтобы заполнять группы внутри направлений
            for group in groups:
                group_name = group.get_text(strip=True) # получаем имя группы, будет ключем
                group_link = "https://pk.mpei.ru/inform/" + group.get('href') # Собираем ссылку на группу

                data[filial][naprav][group_name] = group_link
                

        else:
            print(cells) # Что-то странное, надо посмотреть что именно

    # Здесь формирование списка завершено и надо теперь аккуратненько переписать его в файл

    # Открываем файл с кодировкой utf-8 (для русских букв)
    with open("Stepchik_learn_asynk/links.json", "w", encoding="utf-8") as f:
        # dump(что_пишем, куда_пишем, сохраняем_кириллицу, делаем_отступы)
        json.dump(data, f, ensure_ascii=False, indent=4)



