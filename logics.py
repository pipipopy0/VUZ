import parser as p
import asyncio, aiohttp
import time 
import json



async def check_id_directions(id):
    with open("links.json", "r", encoding = "utf-8") as f:
            data = json.load(f)#это файл со всеми назаваниями направлений и ссылками
            start = time.perf_counter()#засекает время

            try:
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for entry in data:#перебирает все словари в файле
                        for d_name, d_link in entry.items():#перебирает каждый словарь(имя направления - ссылка)
                            task = p.mpei_parser(session=session, id=id, d_link=d_link, d_name=d_name)#тут как раз происходит самый долгий процесс - запрос на сайте
                            tasks.append(task)
                    results = await asyncio.gather(*tasks)

                    for person_dict in results:
                            p_id = person_dict.get("p_id")
                            if str(p_id) == id:
                                p_position = person_dict.get("p_position")
                                p_sum_results = person_dict.get("p_sum_results")
                                d_name = person_dict.get("d_name")
                                d_link = person_dict.get("d_link")
                                print(f"Абитуриент {p_id} на месте {p_position} с баллами {p_sum_results} на направлении {d_name}",f" {d_link} ")
                    end = time.perf_counter()
                    print(f"Выполнение кода потребовало: {end-start:.2f} сек")
            except Exception as e:
                 print(e)