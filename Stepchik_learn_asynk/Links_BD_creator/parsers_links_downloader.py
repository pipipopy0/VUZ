# Файл с парсерами ссылок на направления


def parse_mpei_links(html: str, base_url: str) -> list:
    """Парсит каталог МЭИ, возвращает список ссылок"""
    print(f"🏫 Вуз: НИУ МЭИ")
    print(f"🔗 URL: {base_url}")
    print(f"📄 HTML: {html[:100]}...")  # Первые 100 символов
    
    # Возвращаем заглушку, чтобы конвейер не сломался
    return [{"status": "parsed", "url": base_url}]