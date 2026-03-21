import asyncio
import aiohttp
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import sqlite3

DB_FILE = 'Stepchik_learn_asynk/mpei_links.db'

# Суть ассинхронности: Разложение на части (создал → запустил) дает диспетчеру возможность прыгать между задачами.
# Асинхронность = Диспетчер делает всю работу, но не тратит время на ожидание того, что от него не зависит(прямые задачт ОС).

# Время ожидания для 811 ссылок составляет 45 секунд. После 5-7 одновременных запросов прироста времени нет. Видимо сервер ограничивает количество одновременных загрузок

def get_links_from_db(): # Функция для вытягивания ссылок из БД
    
    conn = sqlite3.connect(DB_FILE) # Подключаемся к базе данных
    coursor = conn.cursor() # Подключаем интерфейс для общения с БД

    query = "SELECT id, form, filial, direction, list_type, url FROM links"
    # Запрос в таблицу. Ключевое слово SELECT потом возвращаемые значения в нужном порядке, в конце пишем из какой таблицы все это вытягивать

    coursor.execute(query) # Отправляем готовый запрос в бд. ВАЖНО: Эта комманда не возвращает полученный результат, а если есть результат, то помещает его в буфер
    rows = coursor.fetchall() # Забираем готовый результат из буфера

    conn.close() # Аккуратно закрываем таблицу после окончания сеанса

    return rows # Возвращаем полученный массив списков




ua = UserAgent() # Создаем случайного фейкового пользователя
async def fetch_page(session, url, semaphore, link_data): # Асинхронная функция для получения списков МЭИ
    
    headers = {"User-Agent": ua.random} # Создаем заголовок, притворяемся пользователем

    async with semaphore:  # ← Ждем своей очереди Чтобы не положить сервер МЭИ
        async with session.get(url, headers=headers) as response: # with гарантирует правильное закрытие соединения, async with то же самое, но для ассинхронных функций, функция возвращает только заголовки, но не код страницы
            html = await response.text() # Запрашиваем код страницы
            return (link_data, html) # Возвращаем полученный результат + здесь же формируем пакет для парсера




async def download_all_pages(queue_html): # Функцяи для скачивания всех страниц с абитуриентами + Помещает скачанные страницы в очередь чтобы не тормозить загрузку
    semaphore = asyncio.Semaphore(15)  # Максимум 5 запросов одновременно
    
    async with aiohttp.ClientSession() as session: # Один клиент на все запросы
        links = get_links_from_db() # Стягиваем ссылки из нашей БД
        
        print(f"📥 Найдено ссылок: {len(links)}")

        tasks = [] # Создаем массив задач для удобства
        for row in links: # Проходимся по каждому кортежу из того что стянули с БД
            link_id, form, filial, direction, list_type, url = row # Распакоувка
            task = fetch_page(session, url, semaphore, row) # Создаем задачу. Важно: без await fetch_page является задачей, а не функцией (по сути само выполнение задачи)
            tasks.append(task)  # Храним список задач

        # results = await asyncio.gather(*tasks) # asyncio.gather() асинхронная функция, которая получает список задач и возвращает результаты их выполнения в том же порядке. Так как стоит await то эта функция выполниться сразу, а не будет висеть задачей. *tasks - распакоувка в параметры, а не указатель
        # Вообще по факту в зависимости от контекста await может интерпретироваться по разному: запусти и ожидай ИЛИ верни результат выполнения ИЛИ запусти, ожидай и верни результат

        i = 1
        for task in asyncio.as_completed(tasks):
            result = await task # <- await Здесь читается как верни результат выполнения
            queue_html.put(result) # Добавляем сырой пакет в очередь на обработку парсеру
            print(f"📊 Прогресс: {i}/{len(tasks)}")
            i += 1

        queue_html.put(None)  # ← Сигнал парсеру: всё, закончил
        

        # for i, html in enumerate(results[:5]):
        #     filename = f"Stepchik_learn_asynk/html/page_{i+1}.html"
        #     with open(filename, "w", encoding="utf-8") as f:
        #         f.write(html)
        #     print(f"💾 Сохранено: {filename}")





if __name__ == "__main__":
    asyncio.run(download_all_pages())