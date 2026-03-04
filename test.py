import asyncio
import aiohttp

# Функция скачивает страницу по URL
async def fetch(session, url):
    print("Скачиваю:", url)
    response = await session.get(url)   # отправляем запрос
    html = await response.text()        # получаем текст страницы
    return html

# Основная функция
async def main():
    urls = [
        "https://example.com",
        "https://python.org",
        "https://github.com"
    ]

    async with aiohttp.ClientSession() as session:
        tasks = []  # сюда будем складывать задачи

        # создаём задачи ОДНА ЗА ДРУГОЙ, без сокращений
        for url in urls:
            task = fetch(session, url)  # создаём задачу
            tasks.append(task)          # кладём в список

        # запускаем все задачи одновременно
        results = await asyncio.gather(*tasks)

        # выводим результат
        for i in range(len(urls)):
            print("URL:", urls[i])
            print("Длина HTML:", len(results[i]))
            print()

# запускаем программу
asyncio.run(main())