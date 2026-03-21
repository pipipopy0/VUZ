import sys
import os
import asyncio
import aiohttp
import time
from statistics import mean
from bs4 import BeautifulSoup
import fake_useragent

# Добавляем родительскую папку в путь поиска модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import Database

# --- Парсер одной страницы ---
async def mpei_parser(session, d_link, id, d_name, sem):
    async with sem:
        try:
            user = fake_useragent.UserAgent().random
            headers = {"user-agent": user}
            async with session.get(d_link, headers=headers) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                p_position = 0
                p_id = None
                p_sum_results = None
                p_priority = None
                all_rowz = soup.find_all("tr")
                for row in all_rowz:
                    get_id = row.get("id")
                    if get_id and get_id[0] == "p":
                        tds = row.find_all("td")
                        p_id = tds[0].text if len(tds) > 0 else None
                        p_sum_results = tds[1].text if len(tds) > 1 else None
                        p_priority = tds[10].text if len(tds) > 10 else None
                        p_position += 1
                        if str(p_id) == id:
                            break
                return {"p_position": p_position,
                        "p_id": p_id,
                        "p_sum_results": p_sum_results,
                        "d_name": d_name,
                        "d_link": d_link,
                        "p_priority": p_priority}
        except Exception as e:
            print(f"Error parsing {d_link}: {e}")
            return {"p_position": None,
                    "p_id": None,
                    "p_sum_results": None,
                    "d_name": d_name,
                    "d_link": d_link,
                    "p_priority": None}

# --- Основная функция поиска абитуриента по ID ---
async def check_id_directions(id, concurrency=20):
    start_total = time.perf_counter()
    dp_path = 'databases/abiturient.db'
    new_dp = Database(dp_path=dp_path)
    data = new_dp.get_all_data()  # получаем все направления

    sem = asyncio.Semaphore(concurrency)  # ограничение параллельных запросов

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        tasks = []
        for entry in data:
            task = mpei_parser(session=session, d_link=entry["link"], id=id, d_name=entry["direction"], sem=sem)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Выводим результат
        found = False
        for person_dict in results:
            p_id = person_dict.get("p_id")
            if str(p_id) == id:
                p_position = person_dict.get("p_position")
                p_sum_results = person_dict.get("p_sum_results")
                d_name = person_dict.get("d_name")
                d_link = person_dict.get("d_link")
                print(f"Абитуриент {p_id} на месте {p_position} с баллами {p_sum_results} на направлении {d_name} {d_link}")
                found = True
        if not found:
            print(f"Абитуриент с ID {id} не найден в списках.")

    end_total = time.perf_counter()
    print(f"Общее время выполнения: {end_total - start_total:.2f} сек")

# --- Точка входа ---
if __name__ == "__main__":
    test_id = "5103917"  # <- замените на нужный ID абитуриента
    asyncio.run(check_id_directions(test_id))