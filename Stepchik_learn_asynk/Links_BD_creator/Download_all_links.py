import asyncio
import json
import aiohttp
from fake_useragent import UserAgent

# from parsers_links_downloader import *  # импортируем парсер(ы)


ua = UserAgent()
SEMAPHORE_LIMIT = 20  # максимум параллельных запросов чтобы не положить мой ноут



def load_config(path: str) -> list: # Функция Для чтения json. Принимает путь до файла.
    with open(path, encoding='utf-8') as file: # Открываем файл для чтения в нужном формате. with гарантирует правильное закрытие файла
        data = json.load(file) # Переносим всю информацию в переменную
    return [u for u in data if u.get('active')] # Возвращаем список вузов, которые мы решили брать



if __name__ == "__main__":
    print(load_config("universities.json"))