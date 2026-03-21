import sqlite3

class Database():
    """Класс будет выполнять всю работу с базами данных
        Атрибуты:
            dp_path (str): путь к файлу базы данных
            dp (sqlite3.Connection): соединение с SQLite
            cursor (sqlite3.Cursor): курсор для выполнения SQL-запросов
            levels (list[tuple]): структура таблиц и колонок для рекурсивной вставки

        Методы:
            create_tables(tables)               - Создаёт таблицы в базе данных.
            add_fixed_data(table, cols, values) - Вставляет данные и возвращает id.
            insert_data(data)                   - Рекурсивно заполняет все таблицы.
            close()                             - Закрывает соединение с базой.
    """

    def __init__(self, dp_path):
        """Инициализация полей класса"""
        self.dp_path = dp_path
        self.dp = sqlite3.connect(self.dp_path)
        self.cursor = self.dp.cursor()
        self.levels = [
            ("universities", ["name_university"]),
            ("forms", ["university_id", "name_form"]),
            ("branches", ["forms_id", "name_branch"]),
            ("directions", ["branch_id", "name_direction"]),
            ("specializations", ["direction_id", "name_specialization", "link_specialization"])
        ]

    def create_tables(self, tables: dict):
        """
        Создаем таблицы по командам, которые передали в параметры функции

        Параметры:
            tables (dict): ключ — имя таблицы, значение - SQL для создания колонок
        """
        try:
            for table_name, command in tables.items():
                self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} ({command})""")
        except Exception as e:
            print(f"Ошибка из create_tables {e}")

    def add_fixed_data(self, table_name: str, column_name_list: list, value_name: list):
        """Записываем в бд фиксированные данные
        
        Параметры:
            table_name (str): имя таблицы
            column_name_list (list[str]): список колонок для вставки
            value_name (list): список значений для колонок

        Возвращает:
            int: id вставленной или существующей строки"""
        try:

            column_name = ",".join(column_name_list)#Соединяет все колонки, чтобы их передать в sql запрос
            questions = ",".join(["?"]*len(value_name))#Делает столько знаков вопроса, сколько мы передаем значений, чтобы передать в sql запрос
            self.cursor.execute(f"""INSERT OR IGNORE INTO {table_name} ({column_name}) VALUES ({questions})""", tuple(value_name))
            """наш sql запрос, который делает вставку или не делает(в случае если уже есть)
            в таблицу(table_name) в колонки(column_name) значения(value_name)
            (value_name) имеет формат кортежа, так как sql принимает кортежи(в круглых скобочках)
            Например (1,2,3,4,5) - кортеж
            """

            where_if = " AND ".join([f"{col}=?" for col in column_name_list])
            """Эта страшная строка делает простую вещь. С помощью метода join она формирует
            условие для последующего sql запроса. Она перебирает все колонки, которые мы передали
            в функцию и делает их в формате 'название колонки=?' и добавляет and между ними
            И у нас получается что-то вроде 'название колонки1=? AND 'название колонки2=?' 
            """
            self.cursor.execute(f"""SELECT id FROM {table_name} WHERE {where_if}""", tuple(value_name))
            return self.cursor.fetchone()[0]
            """ Это нам нужно, для того чтобы мы возвращали id строки, которую только что изменили. 
            Мы этот id потом передаем для связи других таблиц. Вот и все
            """
        except Exception as e:
            print(f"Ошибка из add_fixed_data {e}")
    def insert_recursive(self, data, parent_id = None, level = 0):
        """Рекурсивная функция, чтобы не писать 5 вложенных циклов.
            Она заполняет данные через функцию add_fixed_data()
            
            Параметры:
                data (dict): данные для вставки
                parent_id (int, optional): id родительской записи
                level (int, optional): текущий уровень рекурсии
            """
        try:  
            table_name, columns_name = self.levels[level]
            """Тут мы берем имя таблицы и имя колонок с уровня.
            1-ый table_name = 'universities' columns_name = ["name_university"] и т.д."""
            for key, value in data.items():
                if level == 0:
                    values = [key]
                elif level == 4:
                    values = [parent_id, key, value]
                else:
                    values = [parent_id, key]
            
                row_id = self.add_fixed_data(table_name, columns_name, values)

                if level < len(self.levels) - 1:
                    self.insert_recursive(value, row_id, level+1)
        except Exception as e:
            print(f"Ошибка из insert_recursive {e}")

    def get_all_data(self):
    
        self.cursor.execute("""
        SELECT  universities.name_university, 
                forms.name_form, 
                branches.name_branch, 
                directions.name_direction, 
                specializations.name_specialization, 
                specializations.link_specialization
        
        FROM specializations
                            
        JOIN directions ON specializations.direction_id = directions.id
        JOIN branches ON directions.branch_id = branches.id
        JOIN forms ON branches.forms_id = forms.id
        JOIN universities ON forms.university_id = universities.id                    
        """)

        rows = self.cursor.fetchall()
        result = []

        for u_name, f_name, b_name, d_name, n_s_name, l_n_name in rows:
            result.append({
                        "university": u_name,
                        "form": f_name,
                        "branch": b_name,
                        "direction": d_name,
                        "specialization": n_s_name,
                        "link": l_n_name
                    })
        return result
    def close_dp(self):
        """Очищаем память для всего хорошего"""
        self.dp.commit()
        self.dp.close()