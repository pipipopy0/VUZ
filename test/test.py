import json
import time

with open("C:\\Users\max_k\\OneDrive\\Desktop\VUZ\\Stepchik_learn_asynk\\links.json", "r", encoding="utf-8") as f:
    data = json.load(f)

time1 = time.perf_counter()
for uni_name, forms in data.items():
    print(type(uni_name))
    for form, branches in forms.items():
        for branche, spec_names in branches.items():
            for spec_name, sth in spec_names.items():
                pass
print(time.perf_counter()-time1)


with open("C:\\Users\\max_k\\OneDrive\Desktop\\VUZ\\test\\test.json", "r", encoding="utf-8") as f:
    data = json.load(f)

time1 = time.perf_counter()
for uni_name, forms in data.items():
    print(type(uni_name))
    for form, branches in forms.items():
        print(type(form))
        for branche, spec_names in branches.items():
            print(branche)
            for spec_name, sth in spec_names.items():
                print(type(spec_name))
                for name, link in sth.items():
                    print(type(name))
print(time.perf_counter()-time1)


