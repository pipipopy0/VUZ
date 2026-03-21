import fake_useragent
from bs4 import BeautifulSoup
import aiohttp
import asyncio

user = fake_useragent.UserAgent().random
header = {"user-agent": user}

async def parser(d_link, ):
    async with aiohttp.ClientSession(headers=header) as session:
        async with session.get(d_link) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "lxml")

            # Находим все заголовочные ячейки по твоему тегу
            all_rowz = soup.find_all("td", class_="parName")
            count = -1
            for rows in all_rowz:
                print(rows.text)
                colspan = int(rows.get("colspan", 1))
                count += colspan
                if rows.text == "Приоритет":
                    priority_index = count
                    print(priority_index)
            all_rowz = soup.find_all("tr")
            for row in all_rowz:
                get_id = row.get("id")
                if get_id and get_id[0] == "p":
                    tds = [td.text.strip() for td in row.find_all("td")]
                    for i in range(17):
                        print(tds[i], i)
    

asyncio.run(parser("https://pk.mpei.ru/inform/list533bacc.html"))