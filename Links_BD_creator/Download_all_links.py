import asyncio
import json
import aiohttp
import os
import queue
import threading  
from fake_useragent import UserAgent

from parsers_links_downloader import *  # импортируем парсер(ы)

SEMAPHORE_LIMIT = 20  # максимум параллельных запросов чтобы не положить мой ноут




##############################################################################################
##########                          Работа с сетью                                  ##########
##############################################################################################

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




##############################################################################################
##########                      Сбор ссылок на списки вузов                         ##########
##############################################################################################

def load_config(path: str) -> list: # Функция Для чтения json. Принимает путь до файла.

    base_dir = os.path.dirname(os.path.abspath(__file__)) # Получаем местоположение этого файла файла
    full_path = os.path.join(base_dir, path) # Относительно местоположения ЭТОГо файла ищем файл с сылками

    with open(full_path, encoding='utf-8') as file: # Открываем файл для чтения в нужном формате. with гарантирует правильное закрытие файла
        data = json.load(file) # Переносим всю информацию в переменную
    return [u for u in data if u.get('active')] # Возвращаем список вузов, которые мы решили брать




##############################################################################################
##########                          Скачивание всех страниц                         ##########
##############################################################################################

ua = UserAgent()
async def download_all(unis, queue_html_links):
    """Скачивает HTML и кладёт в очередь"""
    async with aiohttp.ClientSession() as session: # Опять же async with гарантирует правильное закрытие сессии
        semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT) # Это чтобы ноут не положить
        tasks = [] # Массив задач
        
        for uni in unis: # Вытаскиваем все ссылки
            task = asyncio.create_task( # Функция для создания задачи и сразу же запуска ее в фоне. не блокируя выполнение этой функции
                fetch_page(session, uni['base_url'], semaphore, uni)
            )
            tasks.append(task) # Ну и в отдельный массив заносим все запущенные в фоне задачи
        

        for task in asyncio.as_completed(tasks): # По мере выполнения задач
            result = await task # Распаковываем результат выполнения функции
            queue_html_links.put(result)  # ← Кладём в очередь сразу
        
        # Сигнал конца загрузки 
        queue_html_links.put(None)





##############################################################################################
##########                        Выбор правильного парсера                         ##########
##############################################################################################

def get_parser(name: str): # Функция которая к каждому сайту подбирает нужный парсер. Получает имя этого парсера
    """Возвращает функцию-парсер по имени из конфига"""
    parsers = {
        'mpei': parse_mpei_links,
        # 'msu': parse_msu_links,  # добавишь потом
    }
    return parsers.get(name)


##############################################################################################
##########                             Парсинг сайтов                               ##########
##############################################################################################

def parse_worker(queue_html_links, queue_BD_links):
    """Берёт из очереди и обрабатывает"""
    while True: # постоянно крутим цикл парсинга, пока не получим сигнал остановки
        data = queue_html_links.get() 
        
        if data is None:  # ← Сигнал конца 
            queue_BD_links.put(None)  # ← Передаём сигнал остановки дальше
            break # Как раз-таки выход из бесконечного цикла когда скачали и распарсили все что нужно
        
        link_data, html = data # 
        
        if html: # Если пришло что-то осмысленное
            parser_func = get_parser(link_data['parser']) # Выбираем парсер
            
            if parser_func:
                # Вызываем парсер (вот здесь сработает print)
                result = parser_func(html, link_data)
                queue_BD_links.put(result)  # ← Отправляем пачку в БД
            else:
                print(f"❌ Парсер не найден")
        else:
            print(f"❌ Ошибка скачивания: {link_data['name']}")


#################################################################################################
# Заполнение базы данных вузами, филиалами, направлениями, формами обучения и ссылками на списки#
#################################################################################################

import warnings

def db_worker(queue_data):
    """ TODO Заглушка: просто показывает, что приходит от парсера"""
    warnings.warn("⚠️  Download_all_links.py [DB] ЗАГЛУШКА — данные не сохраняются!", UserWarning, stacklevel=2)

    # ЕСЛИ НАДО ТО ЗДЕСЬ МОЖНО СОЗДАТЬ КЛАСС ДЛЯ УПРАВЛЕНИЯ БД
    


    while True:
        data = queue_data.get()
        

        if data is None:  # Сигнал конца
            break
        

        try:
            # Передаём пачку данных в класс
            # ЗДЕСЬ ЗАПИСЫВАЕМ ИНФОРМАЦИЮ ИЗ data В БД
            
            print(f"💾 Сохранено: {len(data)} записей")
            
        except Exception as e:
            print(f"❌ Ошибка БД: {e}")
        


        # Просто выводим то, что пришло
        print(f"💾 [DB] Получено {len(data)} записей:")

        for item in data:  
            print(f"   {item}")
        
    
    print("✅ DB worker завершён")


##############################################################################################
##########                      Дирижер асинхронных функций                         ##########
##############################################################################################

async def star_download_an_parse():
    unis = load_config("universities.json")
    print(f"📋 Вузов: {len(unis)}")


    queue_html_links = queue.Queue(maxsize=50) # Очередь на обработку страниц с ссылками, естественно с ограничением ибо оперативка у меня не бесконечная
    queue_BD_links = queue.Queue(maxsize=50) # Очередь на занесение данных в базу и, естественно с ограничением ибо оперативка у меня не бесконечная

    
    # Запускаем парсера в отдельном потоке
    parser_thread = threading.Thread(target=parse_worker, args=(queue_html_links, queue_BD_links), daemon=True)
    parser_thread.start()

    # Запускаем запись в нашу базу данных в отдельном потоке
    BD_thread = threading.Thread(target=db_worker, args=(queue_BD_links,), daemon=True)
    BD_thread.start()
    
    
    # Запускаем скачивание в asyncio
    await download_all(unis, queue_html_links)
    
    # Ждём завершения парсера
    parser_thread.join()
    BD_thread.join()
    print("✅ Готово")



if __name__ == "__main__":
    asyncio.run(star_download_an_parse())