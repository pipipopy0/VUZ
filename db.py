import sqlite3

class Database():
    """Класс будет выполнять всю работу с базами данных
    """
    def __init__(self, dp_path):
        """Initialization of data fields"""
        self.dp_path = dp_path
        self.dp = sqlite3.connect(self.dp_path)
        self.cursor = self.dp.cursor()
    def create_tables(self, tables: dict):
        """
        Create tables by table_name and command.
        For create indicate
        """
        for table_name, command in tables.items():
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} ({command})""")
    def write_tables(self, file: str, name: dict):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                pass
                #self.cursor.execute(f"""INSERT INTO {}""")

dp_path = 'databases/abiturient.db'

tables = {
        "universities" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_university TEXT""",
        
        "branches" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id INTEGER,
            name_branch TEXT,
            FOREIGN KEY (university_id) REFERENCES universities(id)""",

        "directions" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER,
            name_direction TEXT,
            FOREIGN KEY (branch_id) REFERENCES branches(id)""",

        "specializations" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            directions_id INTEGER,
            name_specialization TEXT,
            link_specialization TEXT,
            FOREIGN KEY (directions_id) REFERENCES directions(id)""",

        
        
        "users" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            social_id INTEGER,
            applicant_id INTEGER""",
        
        "applicantions" : 
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

new_dp = Database(dp_path=dp_path)
new_dp.create_tables(tables=tables)