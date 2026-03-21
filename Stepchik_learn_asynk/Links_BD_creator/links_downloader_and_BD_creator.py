import asyncio
import aiohttp
from fake_useragent import UserAgent
from requests.exceptions import RequestException, HTTPError, Timeout
from bs4 import BeautifulSoup


import sqlite3
# Подключили БД




ua = UserAgent() # Создаем случайного фейкового пользователя
async def fetch_page(session, url, semaphore, link_data): # Асинхронная функция для получения списков МЭИ
    
    headers = {"User-Agent": ua.random} # Создаем заголовок, притворяемся пользователем

    try:
        async with semaphore:  # ← Ждем своей очереди Чтобы не положить мой ноут
            async with session.get(url, headers=headers, timeout=15) as response: # with гарантирует правильное закрытие соединения, async with то же самое, но для ассинхронных функций, функция возвращает только заголовки, но не код страницы
                response.raise_for_status()  # ← 4xx/5xx ошибки
                html = await response.text() # Запрашиваем код страницы
                return (link_data, html) # Возвращаем полученный результат + здесь же формируем пакет для парсера

    except asyncio.TimeoutError:
        print(f"⏱ Таймаут: {url}")
    except aiohttp.ClientResponseError as e:
        print(f"❌ HTTP {e.status}: {url}")
    except aiohttp.ClientConnectorError as e:
        print(f"🔌 Ошибка соединения: {url}")
    except aiohttp.ClientPayloadError as e:
        print(f"📦 Ошибка данных: {url}")
    except Exception as e:
        print(f"⚠️ Неизвестная ошибка: {url} — {type(e).__name__}")
    
    return (link_data, None)  # ← Возвращаем кортеж даже при ошибке













conn = sqlite3.connect('Stepchik_learn_asynk/mpei_links.db') # Открыли или создали файл бд
cursor = conn.cursor() # Указатель, которым тыкаем в базу данных

cursor.execute('''
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form TEXT NOT NULL,
        filial TEXT NOT NULL,
        direction TEXT NOT NULL,
        list_type TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE
    )
''')
conn.commit() # Отфиксировали создание новой таблицы

sql_link_table_isert = """
INSERT OR IGNORE INTO links (form, filial, direction, list_type, url)
VALUES(?, ?, ?, ?, ?)
"""
# Теперь у нас есть удобный шаблон для обращения к нашей таблице

user = UserAgent().random
header = {"user-agent" : user}



def get_safe_html(url):
    try:
        # 2. Запрос с таймаутом (чтобы не висеть вечно)
        response = requests.get(url, headers=header, timeout=10)

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


if __name__ == "__main__":
    # === ПРОВЕРКА ===
    target_url = "https://pk.mpei.ru/inform/entrants_list.html" 

    html_content = get_safe_html(target_url)

    if html_content:
        # Превращаем набор строк в удобное дерево
        soup = BeautifulSoup(html_content, 'lxml')

        # Находим все заголовки форм обучения на странице (идут сверху вниз)
        form_headers = soup.find_all('div', class_='title2')

        # Создаем список только с текстом заголовков
        forms_list = [h.get_text(strip=True) for h in form_headers]
        # Теперь у нас есть список всех форм обучения

        tables = soup.find_all('table', class_='form-grid') # Ищем таблицу с очным бакалавриатом, пока работаем только с ней

        # Так как у нас нет заголовка отдельно от таблицы, то мы можем однозначно сопоставить заголовок с таблицей

        if(len(forms_list) != len(tables)): # Но дополнительная проверочка не помешает, чтобы потом по всему коду не искать
            print("Проблема, размеры получившихся групп не совпадают!") 


        data = {} # Пустой словарь, который заполниться и пойдет в json

        for i in range(len(forms_list)): # Так как размеры массивов одинаковые, то неважно какой брать

            form = forms_list[i] # С какой таблицей работаем(название + таблица)
            table = tables[i]
            data[form] = {} # Ну и сразу сказать что у нас будет такой элемент

            rows = table.find_all('tr') # Разделяем большую таблицу на строки


            filial = "НИУ «МЭИ» г. Москва" # Сначала по умолчанию идет основной вуз который в москве
            data[form][filial] = {}

            for row in rows[1:]: # отдельно обрабатываем каждую строку Кроме первой - там подписи, нам не нужны
                cells = row.find_all('td') # Находим ВСЕ ячейки внутри этой конкретной строки

                if len(cells) == 1: # один столбец = название филиала
                    filial = cells[0].get_text() # Вытягиваем название конкретного филиала
                    data[form][filial] = {}
                    

                elif len(cells) == 2: # два столбца = направление + ссылки
                    # Здесь в первой ячейке лежит направление, а во второй для какой именно группы + ссылки

                    naprav = cells[0].get_text() # Из первой ячейки вытаскиваем название направления
                    groups = cells[1].find_all('a') # Из второй ячейки вытаскиваем массив ссылок с названиями групп

                    data[form][filial][naprav] = {}

                    one_naprav = {} # Массив для того, чтобы заполнять группы внутри направлений
                    for group in groups:
                        group_name = group.get_text(strip=True) # получаем имя группы, будет ключем
                        group_link = "https://pk.mpei.ru/inform/" + group.get('href') # Собираем ссылку на группу

                        data[form][filial][naprav][group_name] = group_link


                        data_sql = (form, filial, naprav, group_name, group_link)
                        # Сформировали кортеж данных для отправки в базу данных
                        cursor.execute(sql_link_table_isert, data_sql)
                        
                else:
                    print(cells) # Что-то странное, надо посмотреть что именно

        conn.commit() # Записали данные в базу данных
        conn.close() # Закрываем базу данных
        # Здесь формирование списка завершено и надо теперь аккуратненько переписать его в файл
        # Открываем файл с кодировкой utf-8 (для русских букв)
        with open("Stepchik_learn_asynk/links.json", "w", encoding="utf-8") as f:
            # dump(что_пишем, куда_пишем, сохраняем_кириллицу, делаем_отступы)
            json.dump(data, f, ensure_ascii=False, indent=4)



