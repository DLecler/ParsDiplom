import threading
import queue
import json
import os
import time
from functools import wraps
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from logger_config import logger

# Глобальные переменные
request_count = 0
result_data = []
result_max_size = 30000
result_size = 0
result_prefix = 0

poepota = ("dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&uclusters=3&uiv=0&"
           "uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-"
           "9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_"
           "U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-"
           "W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular")

catalog_queue = queue.LifoQueue()


def create_session():
    """Создает и возвращает сессию requests с настройками повторных попыток."""
    session = Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[429], allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def send_request(url):
    """Отправляет GET-запрос и обрабатывает ошибки."""
    global request_count
    session = create_session()
    try:
        request_count += 1
        logger.info(f"GET: {url}")
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при запросе {url}: {e}")
        return None

def process_catalog(catalog):

    thread_name = threading.current_thread().name

    url_1 = "https://catalog.wb.ru/catalog/"
    url_2 = "/v8/filters?ab_testing=false&appType=1&"
    url_3 = "&curr=rub&dest=-1255680&hide_dtype=13&lang=ru&&uclusters=3&xsubject="
    url_4 = "&curr=rub&dest=-1255680&filters="
    url_5 = "&curr=rub&dest=-1255680&hide_dtype=13&lang=ru&&uclusters=3"

    time1 = time.time()

    catalogId = catalog.get("id")
    catalogName = catalog.get("name")
    catalogShard = catalog.get("shard")
    catalogQuery = catalog.get("query")
    catalogChilds = catalog.get("childs", [])

    print(f"[{thread_name}] CATALOG: {catalogId} : {catalogName}")

    if catalogChilds:
        print(f"[{thread_name}] Имеются дочерние элементы у каталога {catalogName}, добавляем их в очередь.")
        for child in reversed(catalogChilds):
            catalog_queue.put(child)
        return

    flagFbrandFsupplier = True

    Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_3}{catalogId}")

    filters = Request_DATA.get("data", {}).get("filters", [])
    output_data = []

    items = []
    for f in filters:
        if f.get("key") == "xsubject":
            items = f.get("items", [])

    if items:
        # print(f"[{thread_name}] --ITEMS--")
        for i in items:
            itemId = i.get("id")
            itemName = i.get("name")

            time_ITEM_1 = time.time()

            Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_3}{itemId}")
            filters = Request_DATA.get("data", {}).get("filters", [])
            fullFiltersArr = []
            brandSupplierFilters = []

            for f in filters:
                key = f.get("key")
                if key != "xsubject":
                    Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_4}f{key}")
                    if Request_DATA is None:
                        Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_4}{key}")

                    if Request_DATA:
                        fullFiltersDATA = Request_DATA.get("data", {}).get("filters", [])
                        for fFD in fullFiltersDATA:
                            if fFD.get("key") in ("fbrand", "fsupplier"):
                                if flagFbrandFsupplier:
                                    brandSupplierFilters.append(fFD)
                            else:
                                fullFiltersArr.append(fFD)
                    else:
                        print(f"[{thread_name}] Данных нет")

            time_ITEM_2 = time.time()
            print(f"[{thread_name}] Обработка ITEM {itemId} : {itemName} заняла: {round(time_ITEM_2 - time_ITEM_1)} секунд")

            output_data.append({
                "id": itemId,
                "name": itemName,
                "filters": fullFiltersArr
            })

            if flagFbrandFsupplier:
                flagFbrandFsupplier = False
                brand_supplier_filters_once = {
                    "id": catalogId,
                    "name": catalogName,
                    "filters": brandSupplierFilters
                }

                brand_file_name = f"{catalogName} бренды и продавцы.json"
                brand_file_path = os.path.join('Parametres', brand_file_name)
                if not os.path.exists(brand_file_path):
                    with open(brand_file_path, "w", encoding="utf-8") as f:
                        json.dump([brand_supplier_filters_once], f, ensure_ascii=False, indent=2)
                    # print(f"[{thread_name}] Создан файл: {brand_file_name}")
                    brandSupplierFilters.clear()
    else:
        fullFiltersArr = []
        brandSupplierFilters = []

        Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_5}")
        filters = Request_DATA.get("data", {}).get("filters", [])

        for f in filters:
            key = f.get("key")
            if key != "xsubject":
                Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_5}&filters=f{key}")
                if Request_DATA is None:
                    Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_5}&filters={key}")

                if Request_DATA:
                    fullFiltersDATA = Request_DATA.get("data", {}).get("filters", [])
                    for f in fullFiltersDATA:
                        key = f.get("key")
                        if key in ("fbrand", "fsupplier"):
                            brandSupplierFilters.append(f)
                        else:
                            fullFiltersArr.append(f)
                else:
                    print(f"[{thread_name}] Данных нет")

        output_data = {
            "id": catalogId,
            "name": catalogName,
            "filters": fullFiltersArr
        }

        brand_supplier_filters_once = {
            "id": catalogId,
            "name": catalogName,
            "filters": brandSupplierFilters
        }

        brand_file_name = f"{catalogName} бренды и продавцы.json"
        brand_file_path = os.path.join('Parametres', brand_file_name)
        if not os.path.exists(brand_file_path):
            with open(brand_file_path, "w", encoding="utf-8") as f:
                json.dump([brand_supplier_filters_once], f, ensure_ascii=False, indent=2)
            # print(f"[{thread_name}] Создан файл: {brand_file_name}")
            brandSupplierFilters.clear()

    file_name = f"{catalogName}.json"
    file_path = os.path.join('Parametres', file_name)

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        # print(f"[{thread_name}] Создан файл: {file_name}")

    time2 = time.time()
    print(f"[{thread_name}] Обработка КАТАЛОГА {catalogId} : {catalogName} заняла: {round(time2 - time1)} секунд")
    # print('\n\n\n')



def find_category_with_children(filename: str, category_name: str) -> str:
    """
    Загружает JSON-файл и рекурсивно ищет категорию по точному совпадению названия.
    Возвращает список с найденной категорией и её подкатегориями в формате JSON или пустой список, если не найдено.
    """

    def recursive_search(categories, target_name):
        for category in categories:
            if category.get("name") == target_name:
                return [category]
            if "childs" in category:
                result = recursive_search(category["childs"], target_name)
                if result:
                    return result
        return []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        result = recursive_search(data, category_name)
        return json.dumps(result, ensure_ascii=False, indent=4)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки файла: {e}")
        return json.dumps([])


# def find_category_with_children(filename: str, category_name: str) -> str:
#     """
#     Загружает JSON-файл и рекурсивно ищет категорию по точному совпадению названия.
#     Возвращает только список подкатегорий найденной категории (дерево потомков) в формате JSON.
#     Если категория не найдена или не имеет подкатегорий — возвращает пустой список.
#     """
#
#     def recursive_search(categories, target_name):
#         for category in categories:
#             if category.get("name") == target_name:
#                 return category.get("childs", [])
#             if "childs" in category:
#                 result = recursive_search(category["childs"], target_name)
#                 if result is not None:
#                     return result
#         return None
#
#     try:
#         with open(filename, "r", encoding="utf-8") as file:
#             data = json.load(file)
#
#         result = recursive_search(data, category_name)
#         return json.dumps(result if result is not None else [], ensure_ascii=False, indent=4)
#
#     except (FileNotFoundError, json.JSONDecodeError) as e:
#         print(f"Ошибка загрузки файла: {e}")
#         return json.dumps([])


def all_categories_with_children(filename: str) -> str:
    """
    Загружает JSON-файл и рекурсивно собирает все категории с подкатегориями.
    Возвращает список всех категорий и их подкатегорий в формате JSON.
    """

    def recursive_collect(categories):
        all_categories = []
        for category in categories:
            all_categories.append(category)  # Добавляем текущую категорию
            if "childs" in category:
                all_categories.extend(recursive_collect(category["childs"]))  # Рекурсивно добавляем дочерние категории
        return all_categories

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        result = recursive_collect(data)
        return json.dumps(result, ensure_ascii=False, indent=4)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка загрузки файла: {e}")
        return json.dumps([])




def get_products(list_catalog):
    """Собирает данные о товарах по категориям."""

    global result_data

    for catalog in list_catalog:
        name = catalog.get("name")
        shard = catalog.get("shard")
        query = catalog.get("query")
        childs = catalog.get("childs", [])

        logger.debug(f"Обработка категории: {name}, {shard=}, {query=}")
        print(f"Обработка категории: {name}, {shard=}, {query=}")

        while True:

            print(2)

            # request_url = f"https://catalog.wb.ru/catalog/{shard}/v2/catalog?{query}&page={page}&{poepota}&fcolor=0&xsubject=526"
            request_url = f"https://catalog.wb.ru/catalog/{shard}/v2/catalog?{query}&page=1&{poepota}"

            data = send_request(request_url)

            if not data or "data" not in data:
                logger.error(f"Ошибка загрузки товаров: {name}, 1")
                break

            products = data.get("data", {}).get("products", [])

            process_products(products)
            break

        get_products(childs)

def process_products(products):
    """Обрабатывает список товаров и сохраняет в result_data."""
    global result_data, result_max_size, result_size

    for product in products:
        # result_data.append({
        #     "id": product.get("id"),
        #     "name": product.get("name"),
        #     "brand": product.get("brand"),
        #     "brandId": product.get("brandId"),
        #     "subjectId": product.get("subjectId"),
        #     "supplier": product.get("supplier"),
        #     "supplierId": product.get("supplierId"),
        #
        #     "colors_name": [color.get("name") for color in product.get("colors", [])],
        #     "supplierRating": product.get("supplierRating"),
        #     "rating": product.get("rating"),
        #     "reviewRating": product.get("reviewRating"),
        #     "nmReviewRating": product.get("nmReviewRating"),
        #     "feedbacks": product.get("feedbacks"),
        #     "totalQuantity": product.get("totalQuantity"),
        #
        #     "basic": product.get("sizes", [{}])[0].get("price", {}).get("basic", "None"),
        #     "product": product.get("sizes", [{}])[0].get("price", {}).get("product", "None"),
        #     "total": product.get("sizes", [{}])[0].get("price", {}).get("total", "None"),
        #     "logistics": product.get("sizes", [{}])[0].get("price", {}).get("logistics", "None"),
        # })
        result_data.append(product)
        result_size += len(product.keys())
        # if len(result_data) >= result_max_size:
        #     write_result_file()
        if result_size >= result_max_size:
            write_result_file()


def write_result_file():
    """Записывает собранные данные в JSON-файл."""
    global result_data, result_prefix, result_size

    if not result_data:
        return

    directory_path = "results_parse"
    os.makedirs(directory_path, exist_ok=True)

    file_name = f"result_parse-{result_prefix}.json"
    file_route = os.path.join(directory_path, file_name)

    with open(file_route, 'w', encoding='utf-8') as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)

    result_prefix += 1
    result_size = 0
    result_data = []  # Очищаем список для новых данных



























def worker():
    while not catalog_queue.empty():
        try:
            catalog = catalog_queue.get_nowait()
            process_catalog(catalog)
            catalog_queue.task_done()
        except queue.Empty:
            break

def enqueue_catalogs(catalog):
    if not (catalog.get("childs")):
        catalog_queue.put(catalog)

def get_parametres(list_catalog):

    print(len(list_catalog))

    for catalog in list_catalog:
        enqueue_catalogs(catalog)  # Рекурсивно добавляем всё дерево в очередь

    # Вывод содержимого очереди
    temp_list = list(catalog_queue.queue)
    print("\nТекущая очередь каталогов:")
    for idx, cat in enumerate(reversed(temp_list), 1):
        print(f"{idx}. {cat.get('name', 'Без имени')} (id: {cat.get('id', '-')})")
    print()

    threads = []
    for i in range(5):  # Можно использовать больше потоков, например, 4
        t = threading.Thread(target=worker, name=f"Поток-{i+1}")
        t.start()
        threads.append(t)

    for t in threads:
        t.join()



# if __name__ == "__main__":
#     timeS = time.time()
#
#
#
#     # РЕШИТЬ ПРОБЛЕМУ С ВЫГРУЗКОЙ ВСЕХ ПАРАМЕТРОВ ДЛЯ ОДНОЙ КАТЕГОРИИ, Т.К. СЕЙЧАС РАБОТАЕТ ТОЛЬКО ДЛЯ ВСЕХ КАТЕГОРИЙ В ФАЙЛЕ СРАЗУ
#     # category = find_category_with_children("test_2.json", "Электроника")
#     #
#     # print(category)
#     #
#     # get_parametres(json.loads(category))
#
#
#     category = all_categories_with_children("test_2.json")
#     # print(category)
#     get_parametres(json.loads(category))
#
#     timeF = time.time()
#     print(f"[MAIN] Время работы программы: {round(timeF - timeS)} секунд")
