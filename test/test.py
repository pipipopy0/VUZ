import fake_useragent
from bs4 import BeautifulSoup
import aiohttp
import asyncio

user = fake_useragent.UserAgent().random
header = {"user-agent": user}

async def parser(session, d_link, id, d_name):
    try:
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(d_link) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")

                # Инициализация
                p_position = 0
                p_id = None
                p_sum_results = None
                p_priority = None
                p_remark = None

                # Определяем индексы по заголовкам с учетом colspan
                try:
                    all_rowz = soup.find_all("td", class_="parName")
                    count = -1
                    for rows in all_rowz:
                        colspan = int(rows.get("colspan", 1))
                        count += colspan
                        text = rows.text.strip()
                        if text == "Уникальный код поступающего":
                            id_index = count
                        elif text == "Сумма":
                            score_index = count
                        elif text == "Приоритет":
                            priority_index = count
                        elif text == "Примечание":
                            remark_index = count
                except Exception as e:
                    print("Ошибка при определении индексов заголовков:", e)
                    return None

                # Проходим все строки с id
                try:
                    all_rowz = soup.find_all("tr")
                    for row in all_rowz:
                        get_id = row.get("id")
                        if get_id and get_id[0] == "p":
                            tds = [td.text.strip() for td in row.find_all("td")]

                            p_id = tds[id_index] if len(tds) > id_index else None
                            p_sum_results = tds[score_index] if len(tds) > score_index else None
                            p_priority = tds[priority_index] if len(tds) > priority_index else None
                            p_remark = tds[remark_index] if len(tds) > remark_index else None

                            p_position += 1
                            print(p_position, p_id, p_sum_results, p_priority, p_remark)

                            if str(p_id) == str(target_id):
                                break
                    return {"p_position" : p_position,
                        "p_id" : p_id, 
                        "p_sum_results" : p_sum_results,
                        "d_name" : d_name, 
                        "d_link" : d_link,
                        "p_priority" : p_priority}
                except Exception as e:
                    print("Ошибка при обработке строк данных:", e)
                    return None
    except Exception as e:
        print("Ошибка при запросе страницы:", e)
        return None

# запуск с таблицей
asyncio.run(parser("https://pk.mpei.ru/inform/list533bacc.html", target_id="123456"))