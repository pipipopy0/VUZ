import sqlite3

class Database():
    """Класс будет выполнять всю работу с базами данных
    """
    def __init__(self, dp_path):
        """Инициализация полей класса"""
        self.dp_path = dp_path
        self.dp = sqlite3.connect(self.dp_path)
        self.cursor = self.dp.cursor()
    def create_tables(self, tables: dict):
        """
        Создаем таблицы по командам, которые передали в параметры функции
        """
        for table_name, command in tables.items():
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} ({command})""")

    def add_fixed_data(self, table_name: str, column_name_list: list, value_name: list):
        column_name = ",".join(column_name_list)#Соединяет все колонки, чтобы их передать в sql запрос
        questions = ",".join(["?"]*len(value_name))#Делает столько знаков вопроса, сколько мы передаем значений, чтобы передать в sql запрос
        self.cursor.execute(f"""INSERT OR IGNORE INTO {table_name} ({column_name}) VALUES ({questions})""", tuple(value_name))
        """наш sql запрос, который делает вставку или не делает(в случае если уже есть)
        в таблицу(table_name) в колонки(column_name) значения(value_name)
        (value_name) имеет формат кортежа, так как sql принимает кортежи(в круглых скобочках)
        Например (1,2,3,4,5) - кортеж
        """
        self.dp.commit()#сохраняем изменения

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
    
    def close_dp(self):
        """Очищаем память для всего хорошего"""
        self.dp.close()
                
dp_path = 'databases/abiturient.db'

tables = {
        "universities" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_university TEXT UNIQUE""",
        "forms" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT, 
            university_id INTEGER,
            name_form TEXT,
            FOREIGN KEY (university_id) REFERENCES universities(id)""",
        "branches" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            forms_id INTEGER,
            name_branch TEXT,
            FOREIGN KEY (forms_id) REFERENCES forms(id)""",
        "directions" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER,
            name_direction TEXT,
            FOREIGN KEY (branch_id) REFERENCES branches(id)""",

        "specializations" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            direction_id INTEGER,
            name_specialization TEXT,
            link_specialization TEXT,
            FOREIGN KEY (direction_id) REFERENCES directions(id)""",

        
        
        "users" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            social_id INTEGER,
            applicant_id INTEGER""",
        
        "applications" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            specialization_id INTEGER,
            total_score INTEGER,
            position INTEGER,
            is_agree INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (specialization_id) REFERENCES specializations(id)
            """
            
}

path_file = "C:\\Users\\max_k\\OneDrive\\Desktop\\VUZ\\Stepchik_learn_asynk\\links.json"

new_dp = Database(dp_path=dp_path)
new_dp.create_tables(tables=tables)


with open(path_file, "r", encoding="utf-8") as f:
    import json
    data = json.load(f)

for name_university, forms in data.items():
    university_id = new_dp.add_fixed_data(
        "universities", 
        ["name_university"], 
        [name_university])
    for name_form, branches in forms.items():
        form_id = new_dp.add_fixed_data(
            "forms", 
            ["university_id", "name_form"], 
            [university_id, name_form])
        for name_branch, directions in branches.items():
            branch_id = new_dp.add_fixed_data(
                "branches", 
                ["forms_id", "name_branch"], 
                [form_id, name_branch])
            for name_direction, specializations in directions.items():
                direction_id = new_dp.add_fixed_data(
                    "directions", 
                    ["branch_id", "name_direction"], 
                    [branch_id, name_direction])
                for name_specialization, link_specialization in specializations.items():
                    new_dp.add_fixed_data(
                        "specializations", 
                        ["direction_id", "name_specialization", "link_specialization"], 
                        [direction_id, name_specialization, link_specialization])