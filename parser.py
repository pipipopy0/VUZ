import requests
import json
import fake_useragent
from bs4 import BeautifulSoup

user = fake_useragent.UserAgent().random
header = {"user-agent" : user}

#Ссылки пиздит с мэи
""" Цель: создает файл со всеми названиями и ссылками
    

"""
def parse_links_mpei():
    try:
        link = "https://pk.mpei.ru/inform/entrants_list.html"
        response = requests.get(link, headers=header, timeout=20).text#вот тут мы добавили словарь с заголовком, для того, чтобы имзенить вид user-agent`а
        soup = BeautifulSoup(response, 'lxml')#Он в качесвте аргумента принимает теги html и можно находить с помощью него нужные значение на страницею.
        all_rows = soup.find_all("tr")
        
        data = []#список словарей

        for row in all_rows:
            if row.find("a", class_="competitive-group") and not row.has_attr("style"):
                name = row.find_all("td")[0].text

                all_links = row.find_all("a", class_="competitive-group")

                for links in all_links:
                    second_name = links.text.strip()
                    link = links.get("href")
                    full_name = name + " " + second_name
                    full_link = "https://pk.mpei.ru/inform/" + str(link)
                    data.append({
                        full_name : full_link
                        })

        with open("links.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
                


    except Exception as e:
        print(f"Ошибка {e}")

async def mpei_parser(session, d_link, id, d_name):
    try:
        async with session.get(d_link) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")
            p_position = 0
            p_id = None
            p_sum_results = None
            all_rowz = soup.find_all("tr")
            try:
                for row in all_rowz:
                    get_id = row.get("id")#get_id - это блок, в котором уже есть нужные нам данные. в том числе и уникальный номер
                    if get_id and get_id[0] == "p":     
                        #Тут по идексам нужно находить
                        p_id = row.find_all("td")[0].text#id персонажа
                        p_sum_results = row.find_all("td")[1].text# сумма вступит
                        p_priority = row.find_all("td")[10].text#приоритет среди направлений
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