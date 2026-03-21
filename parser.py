import fake_useragent
from bs4 import BeautifulSoup

user = fake_useragent.UserAgent().random
header = {"user-agent" : user}

async def mpei_parser(session, d_link, id, d_name):
    try:
        async with session.get(d_link) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
            p_position = 0
            p_id = None
            p_sum_results = None
            p_priority = None
            all_rowz = soup.find_all("tr")
            try:
                for row in all_rowz:
                    get_id = row.get("id")#get_id - это блок, в котором уже есть нужные нам данные. в том числе и уникальный номер
                    if get_id and get_id[0] == "p":     
                        #Тут по идексам нужно находить
                        tds = row.find_all("td")
                        p_id = tds[0].text if len(tds) > 0 else None#id персонажа
                        p_sum_results = tds[1].text if len(tds) > 1 else None# сумма вступит
                        p_priority = tds[10].text if len(tds) > 10 else None#приоритет среди направлений
                        p_position += 1
                        if str(p_id) == id:
                            break

                return {"p_position" : p_position,
                        "p_id" : p_id, 
                        "p_sum_results" : p_sum_results,
                        "d_name" : d_name, 
                        "d_link" : d_link,
                        "p_priority" : p_priority}
            except Exception as e:
                print(e)
                return {"p_position": None,
                        "p_id": None,
                        "p_sum_results": None,
                        "d_name" : None,
                        "d_link" : None,
                        "p_priority" : None}
    except Exception as e:
        print(e)
        return {"p_position": None,
                    "p_id": None,
                    "p_sum_results": None,
                    "d_name" : None,
                    "d_link" : None,
                        "p_priority" : None}