# check_urls.py

import sqlite3
from collections import defaultdict

def check_specializations(db_path: str = 'abiturient.db'):
    """Диагностика дублей в таблице specializations"""
    
    print("=" * 70)
    print(f"🔍 ПРОВЕРКА: {db_path}")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Общая статистика
    cursor.execute("SELECT COUNT(*) FROM specializations")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT link_specialization) FROM specializations")
    unique = cursor.fetchone()[0]
    
    print(f"\n📊 Статистика:")
    print(f"   Всего записей: {total}")
    print(f"   Уникальных URL: {unique}")
    print(f"   'Лишних' записей: {total - unique}")
    
    # 2. Проверка на пробелы (невидимые символы)
    cursor.execute("""
        SELECT id, link_specialization, LENGTH(link_specialization) as len, 
               LENGTH(TRIM(link_specialization)) as trimmed_len
        FROM specializations
        WHERE len != trimmed_len
        LIMIT 10
    """)
    whitespace_issues = cursor.fetchall()
    
    if whitespace_issues:
        print(f"\n⚠️  Найдено {len(whitespace_issues)} URL с пробелами/символами:")
        for row_id, url, ln, tr in whitespace_issues:
            print(f"   ID {row_id}: '{url}' [длина: {ln} → {tr}]")
            print(f"   repr: {repr(url)}")
    else:
        print(f"\n✅ Пробелов в начале/конце URL не найдено")
    
    # 3. Группируем дубликаты: какие URL встречаются >1 раза
    cursor.execute("""
        SELECT link_specialization, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
        FROM specializations
        GROUP BY link_specialization
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 20
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n🔗 URL, которые встречаются несколько раз ({len(duplicates)} групп):")
        for url, cnt, ids in duplicates:
            print(f"\n   [{cnt}x] {url}")
            print(f"   IDs: {ids}")
            
            # Показываем контекст: к каким направлениям привязана эта ссылка
            cursor.execute("""
                SELECT d.name_direction, b.name_branch, f.name_form
                FROM specializations s
                JOIN directions d ON s.direction_id = d.id
                JOIN branches b ON d.branch_id = b.id
                JOIN forms f ON b.forms_id = f.id
                WHERE s.link_specialization = ?
                LIMIT 5
            """, (url,))
            contexts = cursor.fetchall()
            print(f"   Контексты:")
            for direction, branch, form in contexts:
                print(f"      • {form} | {branch} | {direction}")
    else:
        print(f"\n✅ Дубликатов по точному совпадению URL не найдено")
    
    # 4. Проверка на "почти дубликаты" (отличаются на 1-2 символа)
    print(f"\n🔎 Поиск 'почти дублей' (разница в 1-2 символа)...")
    
    cursor.execute("SELECT DISTINCT link_specialization FROM specializations")
    all_urls = [row[0] for row in cursor.fetchall()]
    
    # Словарь: очищенный URL → список оригиналов
    normalized = defaultdict(list)
    for url in all_urls:
        # Убираем всё, кроме домена и имени файла
        key = url.split('/')[-1].lower().strip()
        normalized[key].append(url)
    
    suspicious = {k: v for k, v in normalized.items() if len(v) > 1}
    
    if suspicious:
        print(f"⚠️  Найдено {len(suspicious)} групп 'почти дублей':")
        for key, variants in list(suspicious.items())[:10]:
            print(f"\n   Файл: {key}")
            for v in variants:
                print(f"      • '{v}' (len={len(v)})")
    else:
        print(f"✅ 'Почти дублей' не найдено")
    
    # 5. Итоговый вердикт
    print(f"\n" + "=" * 70)
    if total == unique:
        print("🎉 ИДЕАЛЬНО: каждая ссылка встречается ровно 1 раз")
    elif len(whitespace_issues) > 0:
        print("🧹 ПРИЧИНА: пробелы/символы в URL (нужен .strip())")
    elif len(duplicates) > 0:
        print("🔄 ПРИЧИНА: одна ссылка привязана к нескольким направлениям")
        print("   (Это нормально, если схема БД позволяет)")
    else:
        print("❓ ПРИЧИНА: неочевидна, нужна ручная проверка")
    print("=" * 70)
    
    conn.close()
    return {
        'total': total,
        'unique': unique,
        'whitespace': len(whitespace_issues),
        'duplicate_groups': len(duplicates)
    }


if __name__ == "__main__":
    check_specializations('abiturient.db')
    # Если путь другой:
    # check_specializations('Stepchik_learn_asynk/mpei_links.db')