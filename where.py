# clear_db.py

import sqlite3
import os

def clear_database(db_path: str = 'abiturient.db', confirm: bool = True):
    """
    Полностью очищает все таблицы в БД.
    
    ⚠️  Внимание: данные будут удалены безвозвратно!
    """
    
    # Проверка существования файла
    if not os.path.exists(db_path):
        print(f"❌ Файл БД не найден: {db_path}")
        return
    
    # Подтверждение (можно отключить: confirm=False)
    if confirm:
        print(f"⚠️  Ты собираешься удалить ВСЕ данные из '{db_path}'")
        answer = input("Напиши 'YES' для подтверждения: ").strip()
        if answer != 'YES':
            print("✅ Отменено. Данные сохранены.")
            return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Порядок важен: сначала дочерние таблицы (по внешним ключам)
    tables = [
        "specializations",  # зависит от directions
        "directions",       # зависит от branches
        "branches",         # зависит от forms
        "forms",            # зависит от universities
        "universities"      # корень
    ]
    
    print(f"\n🧹 Очистка таблиц...")
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"   • {table}: очищено")
    
    # Сброс автоинкремента (опционально, чтобы ID начинались с 1)
    cursor.execute("DELETE FROM sqlite_sequence")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ БД '{db_path}' полностью очищена")


if __name__ == "__main__":
    # Если путь к БД другой — поменяй здесь
    clear_database('abiturient.db')
    # Или: clear_database('Stepchik_learn_asynk/mpei_links.db')