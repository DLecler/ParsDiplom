# import json
#
# def extract_parents(categories):
#     parents = []
#
#     for category in categories:
#         if "childs" in category and category["childs"]:
#             # Сохраняем только id и name
#             parents.append({
#                 "id": category["id"],
#                 "name": category["name"]
#             })
#             # Рекурсивно ищем родителей в дочерних категориях
#             parents.extend(extract_parents(category["childs"]))
#
#     return parents
#
# # Чтение исходного файла
# with open("Categories_and_childs_new.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# # Извлечение родителей
# parent_categories = extract_parents(data)
#
# # Запись в файл b.json
# with open("MainCategories.json", "w", encoding="utf-8") as f:
#     json.dump(parent_categories, f, ensure_ascii=False, indent=4)






import json

# Чтение исходного файла
with open("Categories_and_childs_new.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Извлечение родителей первого уровня
parent_categories = [
    {"id": category["id"], "name": category["name"]}
    for category in data
    if "childs" in category and category["childs"]
]

# Запись в файл b.json
with open("MainCategories.json", "w", encoding="utf-8") as f:
    json.dump(parent_categories, f, ensure_ascii=False, indent=4)

print("Родители первого уровня сохранены в b.json")
