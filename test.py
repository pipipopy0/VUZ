import requests
import json
import fake_useragent
from bs4 import BeautifulSoup

user = fake_useragent.UserAgent().random
header = {"user-agent" : user}
#tr, td, a, competitive_group, style
"""mpei_config = {
    "link" : "https://pk.mpei.ru/inform/entrants_list.html",
    "all_rows_tag" : "tr",
    "row_" :  "",
}"""

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