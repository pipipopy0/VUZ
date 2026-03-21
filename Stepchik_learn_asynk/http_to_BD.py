import asyncio
import threading
import queue

from downloader_abiturients import download_all_pages



def convert_server_to_BD():
    """
    Дирижёр конвейера: Скачивание → Парсинг → Запись в БД
    """
    # 1. Создаём очереди
    # 2. Запускаем потоки (парсер, БД)
    # 3. Запускаем скачивание
    # 4. Ждём завершения всех

    queue_html = queue.Queue(maxsize=50) # Очередь для скачанных html страниц
    queue_data = queue.Queue(maxsize=100) # Очередь для сформированных пакетов в бд

    parser_thread = threading.Thread(target=parse_worker, args=(queue_html, queue_data), daemon=True) # Создали поток, но не запустили его (как с задачами в асинхронном)
    parser_thread.start() # Запускаем параллельный поток для работы парсера
    
    # db_thread = threading.Thread(target=db_worker, args=(queue_data,), daemon=True) # Порядок аргументов: Функция для которой создается параллельный поток, аргументы. которые будут переданы в функцию, Демон, чтобы знать зависит жизнь этого потока от основного или нет
    # db_thread.start()



    #  Запускаем скачивание (блокирует главный поток, пока не скачает всё)
    asyncio.run(download_all_pages(queue_html))

    parser_thread.join() # Подождем пока парсер закончит свою работу
    # db_thread.join() # Ждем окончания работы функции управления БД


def parse_worker(q_in, q_out):
    """
    Парсер: берёт HTML из очереди, отдаёт данные в следующую очередь.
    Пока просто печатает, что получил данные.
    """
    print("🔧 Парсер запущен...")
    
    while True:
        item = q_in.get()  # ← Ждёт данные из очереди (блокируется)
        
        if item is None:  # ← Сигнал конца
            q_out.put(None)  # ← Передаём сигнал дальше
            print("⏹ Парсер получил сигнал завершения")
            break
        
        
        # TODO: Тут будет реальный парсинг
        # Распаковываем данные
        link_data, html = item

        # link_data это кортеж: (id, form, filial, direction, list_type, url)
        link_id, form, filial, direction, list_type, url = link_data

        # TODO: Тут будет реальный парсинг
        print(f"📄 Получено:")
        print(f"   link_id={link_id}")
        print(f"   форма={form}")
        print(f"   филиал={filial}")
        print(f"   направление={direction}")
        print(f"   тип={list_type}")
        print(f"   HTML (первые 100 симв): {html[:100]}...")
        
        # TODO: Тут парсер положит распарсенные данные в q_out
        # q_out.put((link_data, students))
    
    print("⏹ Парсер завершил работу")


if __name__ == "__main__":
    convert_server_to_BD()


