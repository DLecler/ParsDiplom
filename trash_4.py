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

# URL API Wildberries
# back_api_host = "https://catalog.wb.ru"

# Параметры запроса
# poepota = ("dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&spp=30&uclusters=3&uiv=0&"
#            "uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-"
#            "9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_"
#            "U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-"
#            "W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular")

poepota = ("dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&uclusters=3&uiv=0&"
           "uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-"
           "9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_"
           "U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-"
           "W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular")


# "https://catalog.wb.ru/catalog/electronic36/v2/catalog?cat=9509&page=1&dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&uclusters=3&uiv=0&uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular"

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


# def get_main_catalog_children(categoryName):
#     """Получает список подкатегорий каталога 'Электроника' из локального файла Categories_and_childs.json."""
#     try:
#         with open("Categories_and_childs.json", "r", encoding="utf-8") as file:
#             catalogs = json.load(file)  # Загружаем JSON-данные из файла
#     except (FileNotFoundError, json.JSONDecodeError) as e:
#         logger.error(f"Ошибка при загрузке файла Categories_and_childs.json: {e}")
#         return []
#
#     for catalog in catalogs:
#         if catalog.get("name") == categoryName:
#             logger.info(f"Категория {categoryName} успешно загружена")
#             print(catalog.get("childs"))
#             return catalog.get("childs", [])
#
#     return []

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


def get_parametres(list_catalog):

    url_1 = "https://catalog.wb.ru/catalog/"
    url_2 = "/v8/filters?ab_testing=false&appType=1&"
    url_3 = "&curr=rub&dest=-1255680&hide_dtype=13&lang=ru&&uclusters=3&xsubject="
    url_4 = "&curr=rub&dest=-1255680&filters="
    url_5 = "&curr=rub&dest=-1255680&hide_dtype=13&lang=ru&&uclusters=3"

    stack = list_catalog[::-1]

    while stack:

        time1 = time.time()

        catalog = stack.pop()

        catalogId = catalog.get("id")
        catalogName = catalog.get("name")
        catalogShard = catalog.get("shard")
        catalogQuery = catalog.get("query")
        catalogChilds = catalog.get("childs", [])

        print(f"CATALOG: {catalogId} : {catalogName}")

        if catalogChilds:
            print(f"Имеются дочерние элементы у каталога {catalogName}, добавляем их в очередь.")
            stack.extend(catalogChilds[::-1])
            continue

        flagFbrandFsupplier = True

        Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_3}{catalogId}")

        filters = Request_DATA.get("data", {}).get("filters", [])
        output_data = []

        items = []

        for f in filters:
            if f.get("key") == "xsubject":
                items = f.get("items", [])

        if (items):
            print("--ITEMS--")
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
                            fullFiltersDATA = Request_DATA["data"]["filters"]
                            for fFD in fullFiltersDATA:
                                if fFD.get("key") in ("fbrand", "fsupplier"):
                                    if (flagFbrandFsupplier):
                                        brandSupplierFilters.append(fFD)
                                else:
                                    fullFiltersArr.append(fFD)
                        else:
                            print("Данных нет")

                time_ITEM_2 = time.time()

                print(f"Обработка ITEM {itemId} : {itemName} заняла: {round(time_ITEM_2 - time_ITEM_1)} секунд")

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
                        print(f"Создан файл: {brand_file_name}")
                        brandSupplierFilters.clear()


        else:

            fullFiltersArr = []
            brandSupplierFilters = []

            Request_DATA = send_request(f"{url_1}{catalogShard}{url_2}{catalogQuery}{url_5}")
            filters = Request_DATA.get("data", {}).get("filters", [])
            #
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
                        print("Данных нет")

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
                print(f"Создан файл: {brand_file_name}")
                brandSupplierFilters.clear()



        file_name = f"{catalogName}.json"
        file_path = os.path.join('Parametres', file_name)

        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"Создан файл: {file_name}")
            fullFiltersArr.clear()

        time2 = time.time()
        print(f"Обработка КАТАЛОГА {catalogId} : {catalogName} заняла: {round(time2 - time1)} секунд")
        print('\n\n\n')



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

# category = find_category_with_children("test_2.json", "Электроника")

timeS = time.time()
category = find_category_with_children("test_2.json", "Электроника")
# category = find_category_with_children("test_1.json", "Юбки")
print(category)
# get_products(json.loads(category))
get_parametres(json.loads(category))

# write_result_file()

timeF = time.time()
print(f"Время работы программы: {round(timeF-timeS)}")