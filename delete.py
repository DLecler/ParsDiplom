import json

def clean_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def remove_keys(obj):
        if isinstance(obj, dict):
            return {k: remove_keys(v) for k, v in obj.items() if k not in ("id")}
        elif isinstance(obj, list):
            return [remove_keys(item) for item in obj]
        else:
            return obj

    cleaned_data = remove_keys(data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

clean_json_file("Categories_and_childs_clear.json")



# import json
#
# def collect_keys(obj, keys_set):
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             keys_set.add(key)
#             collect_keys(value, keys_set)
#     elif isinstance(obj, list):
#         for item in obj:
#             collect_keys(item, keys_set)
#
# with open("Categories_and_childs_new.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# unique_keys = set()
# collect_keys(data, unique_keys)
#
# for key in sorted(unique_keys):
#     print(f'"{key}"')

