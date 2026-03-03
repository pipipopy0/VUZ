import parser as p
import time 
import json



if __name__ == "__main__":
    id = input()
    with open("links.json", "r", encoding = "utf-8") as f:
        data = json.load(f)
        start = time.perf_counter()#засекает время
        for entry in data:#перебирает все словари
            for name, link in entry.items():
                person_dict = p.mpei_parser(id=id, link=link)
                p_position = person_dict.get("p_position")
                p_sum_results = person_dict.get("p_sum_results")
                p_id = person_dict.get("p_id")
                if str(p_id) == id:
                    print(f"Абитуриент {p_id} на месте {p_position} с баллами {p_sum_results} на направлении {name}",f" {link} ")
        end = time.perf_counter()
        print(f"Выполнение кода потребовало: {end-start:.2f} сек")
            
            