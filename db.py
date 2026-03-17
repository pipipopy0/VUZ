import sqlite3

class Database():
    """
    Инициализация полей класса
    Класс будет выполнять всю работу с базами данных
    """
    def __init__(self, dp_path = 'databases/abiturient.db'):
        self.dp_path = dp_path
        self.dp = sqlite3.connect(self.dp_path)
        self.cursor = self.dp.cursor()
    def create_tables(self, tables: dict):
        for table_name, command in tables.items():
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} ({command})""")


tables = {
        "universities" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_university TEXT""",
        
        "branches" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id INTEGER,
            name_branch TEXT,
            FOREIGN KEY (university_id) REFERENCES universities(id)""",

        "specialization" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER,
            name_specialization TEXT,
            link_specialization TEXT,
            FOREIGN KEY (branch_id) REFERENCES branches(id)"""
}
