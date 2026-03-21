from db import Database
import json


dp_path = 'databases/abiturient.db'

tables = {
        "universities" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_university TEXT UNIQUE""",
        "forms" :
            """id INTEGER PRIMARY KEY AUTOINCREMENT, 
            university_id INTEGER,
            name_form TEXT,
            UNIQUE (university_id, name_form),
            FOREIGN KEY (university_id) REFERENCES universities(id)""",
        "branches" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            forms_id INTEGER,
            name_branch TEXT,
            UNIQUE (forms_id, name_branch),
            FOREIGN KEY (forms_id) REFERENCES forms(id)""",
        "directions" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_id INTEGER,
            name_direction TEXT,
            UNIQUE (branch_id, name_direction),
            FOREIGN KEY (branch_id) REFERENCES branches(id)""",

        "specializations" : 
            """id INTEGER PRIMARY KEY AUTOINCREMENT,
            direction_id INTEGER,
            name_specialization TEXT,
            link_specialization TEXT,
            UNIQUE (direction_id, name_specialization, link_specialization),
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
            priority INTEGER,
            is_agree INTEGER,
            remark TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (specialization_id) REFERENCES specializations(id)
            """
            
}

path_file = "C:\\Users\\max_k\\OneDrive\\Desktop\\VUZ\\Stepchik_learn_asynk\\links.json"

new_dp = Database(dp_path=dp_path)
new_dp.create_tables(tables=tables)

with open(path_file, "r", encoding='utf-8') as f:
    data = json.load(f)

new_dp.insert_recursive(data=data)

new_dp.close_dp()