import fake_useragent
from bs4 import BeautifulSoup
import aiohttp

user = fake_useragent.UserAgent().random
header = {"user-agent" : user}

async def mpei_parser(d_link, id, d_name):
    try:
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(d_link) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")

                # Определяем индексы по заголовкам с учетом colspan
                id_index = score_index = priority_index = remark_index = None
                try:
                    header_row = soup.find("table").find("tr")  # первая строка таблицы
                    col_counter = 0
                    for td in header_row.find_all("td"):
                        colspan = int(td.get("colspan", 1))
                        text = td.text.strip()
                        if text == "Уникальный код поступающего":
                            id_index = col_counter
                        elif text == "Сумма":
                            score_index = col_counter
                        elif text == "Приоритет":
                            priority_index = col_counter
                        elif text == "Примечание":
                            remark_index = col_counter
                        col_counter += colspan
                except Exception as e:
                    print("Ошибка при определении индексов заголовков:", e)
                    return {
                        "p_position": None,
                        "p_id": None,
                        "p_sum_results": None,
                        "d_name": d_name,
                        "d_link": d_link,
                        "p_priority": None
                    }

                # Проходим все строки данных
                p_position = 0
                p_id = p_sum_results = p_priority = None
                try:
                    all_rows = soup.find_all("tr")
                    for row in all_rows:
                        get_id = row.get("id")
                        if get_id and get_id[0] == "p":
                            tds = [td.text.strip() for td in row.find_all("td")]
                            p_id = tds[id_index] if id_index is not None and len(tds) > id_index else None
                            p_sum_results = tds[score_index] if score_index is not None and len(tds) > score_index else None
                            p_priority = tds[priority_index] if priority_index is not None and len(tds) > priority_index else None

                            p_position += 1

                            if str(p_id) == str(id):
                                break
                except Exception as e:
                    print("Ошибка при обработке строк данных:", e)
                    return {
                        "p_position": None,
                        "p_id": None,
                        "p_sum_results": None,
                        "d_name": d_name,
                        "d_link": d_link,
                        "p_priority": None
                    }

                return {
                    "p_position": p_position,
                    "p_id": p_id,
                    "p_sum_results": p_sum_results,
                    "d_name": d_name,
                    "d_link": d_link,
                    "p_priority": p_priority
                }

    except Exception as e:
        print("Ошибка при запросе страницы:", e)
        return {
            "p_position": None,
            "p_id": None,
            "p_sum_results": None,
            "d_name": d_name,
            "d_link": d_link,
            "p_priority": None
        }