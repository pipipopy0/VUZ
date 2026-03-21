# Файл с парсерами ссылок на направления
"""
Формат возвращаемых Значений:

[
    {
        'university': 'НИУ МЭИ',        # Из link_data['name']
        'form': 'Очная',                # Из HTML или link_data
        'filial': 'Москва',             # Из HTML (заголовок)
        'direction': '09.03.02 Информатика',  # Из HTML (таблица)
        'list_type': 'Без ВИ',          # Из HTML (тип списка)
        'url': 'https://pk.mpei.ru/...' # Из HTML (полная ссылка)
    },
    ...
]

"""


from bs4 import BeautifulSoup


def parse_mpei_links(html: str, link_data: str) -> list:
    """Парсит каталог МЭИ, возвращает список ссылок"""
    print(f"🏫 Вуз: НИУ МЭИ")
    print(f"🔗 URL: {link_data}")
    print(f"📄 HTML: {html[:100]}...")  # Первые 100 символов
    
    # 1. Превращаем строку в дерево
    soup = BeautifulSoup(html, 'lxml')

    # 2. Находим заголовки форм обучения
    form_headers = soup.find_all('div', class_='title2')
    forms_list = [h.get_text(strip=True) for h in form_headers]
    print(f"🔍 Найдено форм: {len(forms_list)} — {forms_list}")

    # 3. Находим таблицы с направлениями
    tables = soup.find_all('table', class_='form-grid')
    print(f"🔍 Найдено таблиц: {len(tables)}")

    # 4. Проверка на рассинхрон
    if len(forms_list) != len(tables):
        print(f"❌ Рассинхрон: форм {len(forms_list)}, таблиц {len(tables)}")
        return []

    results = []  # ← Сюда будем собирать найденные ссылки

    # 5. Проходим по парам (Форма → Таблица)
    for form, table in zip(forms_list, tables): # zip составляет как раз-таки эти пары
        print(f"  📚 Форма: {form}")
        
        # По умолчанию филиал — главный вуз
        filial = "НИУ «МЭИ» г. Москва"
        
        # Берем все строки таблицы, пропускаем первую (шапку)
        rows = table.find_all('tr')[1:]
        
        for row in rows:
            cells = row.find_all('td')
            
            # Пока просто выводим структуру для отладки
            if len(cells) == 1:
                print(f"    🏢 Филиал: {cells[0].get_text(strip=True)}")
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
                        
                        # Формируем итоговый словарь
                        results.append({
                            'university': link_data['name'],
                            'form': form,
                            'filial': filial,
                            'direction': direction,
                            'list_type': list_type,
                            'url': full_url
                        })
    
    return results