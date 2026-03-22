# Файл с парсерами ссылок на направления
"""
Формат возвращаемых Значений:

{
    "НИУ МЭИ": {
        "Бакалавриат очная форма обучения": {
            "НИУ «МЭИ» г. Москва": {
                "Направление...": {
                    "Без ВИ": "https://...",
                    "Целевики": "https://..."
                }
            }
        }
    }
}

"""

##############################################################################################
##########                        Выбор правильного парсера                         ##########
##############################################################################################

def get_parser(name: str): # Функция которая к каждому сайту подбирает нужный парсер. Получает имя этого парсера
    """Возвращает функцию-парсер по имени из конфига"""
    parsers = {
        'mpei': parse_mpei_links,
        'mipt': parse_mipt_links,
        # 'msu': parse_msu_links,  # добавишь потом
    }
    return parsers.get(name)


##############################################################################################
##########                               Сами парсеры                               ##########
##############################################################################################


from bs4 import BeautifulSoup
import re



def parse_mpei_links(html: str, link_data: dict) -> dict:
    """Парсит каталог МЭИ, возвращает список ссылок"""
    # print(f"🏫 Вуз: НИУ МЭИ")
    # print(f"🔗 URL: {link_data}")
    # print(f"📄 HTML: {html[:100]}...")  # Первые 100 символов
    
    # 1. Превращаем строку в дерево
    soup = BeautifulSoup(html, 'lxml')

    # 2. Находим заголовки форм обучения
    form_headers = soup.find_all('div', class_='title2')
    forms_list = [h.get_text(strip=True) for h in form_headers]
    # print(f"🔍 Найдено форм: {len(forms_list)} — {forms_list}")

    # 3. Находим таблицы с направлениями
    tables = soup.find_all('table', class_='form-grid')
    # print(f"🔍 Найдено таблиц: {len(tables)}")

    # 4. Проверка на рассинхрон
    if len(forms_list) != len(tables):
        print(f"❌ Рассинхрон: форм {len(forms_list)}, таблиц {len(tables)}")
        return {}

    
    # results = []

    # Итоговое дерево
    results = {}

    # Название университета
    university = link_data['name']

    # По умолчанию филиал — главный вуз
    filial = "НИУ «МЭИ» г. Москва"


    # 5. Проходим по парам (Форма → Таблица)
    for form, table in zip(forms_list, tables): # zip составляет как раз-таки эти пары
        # print(f"  📚 Форма: {form}")
        
        
    
        # Берем все строки таблицы, пропускаем первую (шапку)
        rows = table.find_all('tr')[1:]
        
        for row in rows:
            cells = row.find_all('td')
            
            # Названия филиалов занимают всю строку
            if len(cells) == 1:
                filial = cells[0].get_text(strip=True)
                # print(f"    🏢 Филиал: {cells[0].get_text(strip=True)}")
            elif len(cells) == 2:
                
                # Ячейка с направлением и ссылками
                direction = cells[0].get_text(strip=True)
                
                # Во второй ячейке — ссылки на списки
                groups = cells[1].find_all('a')
                
                for group in groups:
                    list_type = group.get_text(strip=True)  # "Без ВИ", "Целевики"
                    href = group.get('href')
                    
                    if href:
                        # Собираем полный URL
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = "https://pk.mpei.ru/inform/" + href.lstrip('/')
                        

                        # # Формируем итоговый словарь
                        # results.append({
                        #     'university': link_data['name'],
                        #     'form': form,
                        #     'filial': filial,
                        #     'direction': direction,
                        #     'list_type': list_type,
                        #     'url': full_url
                        # })

                        # Убираем только "список поступающих на", оставляем "по"
                        list_type = re.sub(r'^список поступающих на\s*', '', list_type, flags=re.IGNORECASE)

                        # 1. Извлекаем ID из ссылки (например, "2218" из "...list2218.html")
                        link_id = full_url.rstrip('.html').split('_')[-1] if '_' in full_url else '0'

                        # 2. Добавляем ID к названию типа списка
                        unique_key = f"{list_type} #{link_id}"

                       # 🌲 Строим дерево
                        results.setdefault(university, {}) \
                               .setdefault(form, {}) \
                               .setdefault(filial, {}) \
                               .setdefault(direction, {})[unique_key] = full_url
    
    return results



import json


def parse_mipt_links(html: str, link_data: dict) -> dict:
    """Парсит каталог МФТИ, возвращает список ссылок"""
    
   # 1. Превращаем строку в дерево
    soup = BeautifulSoup(html, 'lxml')

    # 2. Находим все таблицы
    tables = soup.find_all('table')

    # Название вуза
    university = link_data['name'] 
    # А филиал здесь только один
    filial = "Основной кампус"
    # Накаких форм кроме очной нет
    form = "Очная"

    # Переменная для хранения результатов (итоговое дерево)
    results = {}

    for table in tables:

        # Извлекаем все строки
        rows = table.find_all('tr')

        # Обрезаем шапку
        rows = table.find_all('tr')[1:]

        # Переменная для хранения направления подготовки
        naprav = "" 

        

        for row in rows: # Проходимся по каждой строке таблицы

            # Извлекаем из строки столбцы
            cells = row.find_all('td')

            if len(cells) == 1: # В этих ячейках есть направления подготовки

                if "Программы" in cells[0].get_text(): # Это для нас бесполезная строка
                    continue
                naprav = cells[0].get_text()

            elif len(cells) == 4: # Где-то здесь живут списки

                progr = cells[0].get_text() # В первой ячейке находиться программа
                
                for cell in cells[1:]: # Проходимся по всем ячейкам

                    # Собираем все ссылки
                    links = cell.find_all('a', href=True)

                    for link in links: # Теперь обрабатываем каждую ссылку (если они вообще есть)
                        
                        # Тип списка
                        list_type = link.get_text(strip=True)

                        # Собственна ссылка
                        href = link.get('href')

                        direction = naprav + " — " + progr

                       # 🌲 Строим дерево
                        results.setdefault(university, {}) \
                               .setdefault(form, {}) \
                               .setdefault(filial, {}) \
                               .setdefault(direction, {})[list_type] = href
    
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results







