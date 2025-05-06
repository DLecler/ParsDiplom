# import json
# import os
#
# from requests import Session
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
#
# import logging
#
# logging.basicConfig(
#     filename='wb_parse.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',  # Добавлен формат даты
#     encoding='utf-8'  # Кодировка для корректной работы с кириллицей
# )
#
# retries = Retry(
#     total=5,
#     backoff_factor=2,
#     status_forcelist=[429],
#     allowed_methods=["GET"]
# )
#
# request_count = 0
#
# result_data = []
# result_max_size = 5000
# result_prefix = 0
#
# back_api_host = "https://catalog.wb.ru"
# poepota = "dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&spp=30&uclusters=3&uiv=0&uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular"
#
# def write_result_file(result_data, result_prefix):
#     directory_path = "results_parse"
#     if not os.path.exists(directory_path):
#         os.makedirs(directory_path)
#
#     file_name = f"result_parse-{result_prefix}.json"
#     file_route = os.path.join(directory_path, file_name)
#     with open(f'{file_route}', 'w', encoding='utf-8') as file:
#         json.dump(result_data, file, indent=4, ensure_ascii=False)
#
#
# def get_main_catalog_children():
#     global request_count
#     session = Session()
#     session.mount('https://', HTTPAdapter(max_retries=retries))
#     session.mount('http://', HTTPAdapter(max_retries=retries))
#     try:
#         request_count += 1
#         catalog_response = session.get("https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json")
#         catalog_response.raise_for_status()
#     except Exception as e:
#         logging.error(f"Ошибка: {e}")
#
#     calalogs = json.loads(catalog_response.content)
#
#     main_calalog_childs = []
#     for main_calalog in calalogs:
#         main_clg_name = main_calalog.get("name")
#         if main_clg_name == "Электроника":
#             main_calalog_childs = main_calalog.get("childs")
#             break
#     logging.info(f"success get catalog_childs")
#     return main_calalog_childs
#
#
# def get_products(list_catalog, page):
#     global request_count, result_prefix, result_data
#
#     for main_calalog_child in list_catalog:
#         query = main_calalog_child.get("query")
#         name = main_calalog_child.get("name")
#         shard = main_calalog_child.get("shard")
#         # print(f"Process with {name = }; {shard = } / {query = }")
#         logging.debug(f"Process with {name = }; {shard = } / {query = }")
#         childs = main_calalog_child.get("childs", [])
#         main_success = True
#         while main_success:
#             page += 1
#             request_url = f"{back_api_host}/catalog/{shard}/v2/catalog?{query}&{page=}&{poepota}"
#             session = Session()
#             session.mount('https://', HTTPAdapter(max_retries=retries))
#             session.mount('http://', HTTPAdapter(max_retries=retries))
#             try:
#                 request_count += 1
#                 logging.info(f"GET: {request_url}")
#                 response = session.get(request_url)
#                 response.raise_for_status()
#             except Exception as e:
#                 logging.error(f"Ошибка: {e}")
#
#             if response.status_code != 200:
#                 main_success = False
#                 logging.error(f"status = {response.status_code}, {response.reason}, {page = }, {response.url = }")
#                 continue
#             if response.content:
#                 data = json.loads(response.content).get("data")
#                 if data:
#                     products = data.get("products", [])
#                     if products:
#                         for product in products:
#                             product_id = product.get("id")
#                             brand = product.get("brand")
#                             brand_id = product.get("brandId")
#                             colors = product.get("colors")
#                             colors_name = []
#                             for color in colors:
#                                 color_name = color.get("name")
#                                 colors_name.append(color_name)
#                             subject_id = product.get("subjectId")
#                             name = product.get("name")
#                             supplier = product.get("supplier")
#                             supplier_id = product.get("supplierId")
#                             supplier_rating = product.get("supplierRating")
#                             rating = product.get("rating")
#                             review_rating = product.get("reviewRating")
#                             nm_review_rating = product.get("nmReviewRating")
#                             feedbacks = product.get("feedbacks")
#                             total_quantity = product.get("totalQuantity")
#
#                             basic = "None"
#                             product_price = "None"
#                             total = "None"
#                             logistics = "None"
#                             sizes = product.get("sizes", [])
#                             for size_dict in sizes:
#                                 price_dict = size_dict.get("price", {})
#                                 basic = price_dict.get("basic")
#                                 product_price = price_dict.get("product")
#                                 total = price_dict.get("total")
#                                 logistics = price_dict.get("logistics")
#
#                             logging.debug(f"Process with {name = } {brand = } / {total = }")
#
#                             results = {
#                                 "id": product_id,
#                                 "brand": brand,
#                                 "colors_name": colors_name,
#                                 "name": name,
#                                 "brand_id": brand_id,
#                                 "subject_id": subject_id,
#                                 "supplier": supplier,
#                                 "supplier_id": supplier_id,
#                                 "supplier_rating": supplier_rating,
#                                 "rating": rating,
#                                 "review_rating": review_rating,
#                                 "nm_review_rating": nm_review_rating,
#                                 "feedbacks": feedbacks,
#                                 "total_quantity": total_quantity,
#                                 "basic": basic,
#                                 "product": product_price,
#                                 "total": total,
#                                 "logistics": logistics,
#                             }
#                             result_data.append(results)
#                             if len(result_data)  >= result_max_size:
#                                 write_result_file(result_data, result_prefix)
#                                 result_prefix += 1
#                                 result_data = []
#                 else:
#                     logging.error(f"{data = }, {request_url = } {childs = }")
#         get_products(childs, 0)
#
#
# main_catalog_child = get_main_catalog_children()
# get_products(main_catalog_child, 0)
# write_result_file(result_data, result_prefix)
#
# logging.info(f"Final with {request_count = }")




























import json  # Импортируем модуль json для работы с JSON-данными
import os  # Импортируем модуль os для работы с файловой системой

# Импортируем библиотеку requests для выполнения HTTP-запросов
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry  # Используется для повторных попыток запросов в случае ошибок

from logger_config import logger

# Настройка повторных попыток HTTP-запросов
retries = Retry(
    total=5,  # Общее количество повторных попыток
    backoff_factor=2,  # Время ожидания перед повторной попыткой (экспоненциальный рост)
    status_forcelist=[429],  # Перезапрашиваем только при HTTP-статусе 429 (слишком много запросов)
    allowed_methods=["GET"]  # Ограничение на методы запросов (только GET)
)

# Глобальные переменные
request_count = 0  # Количество отправленных запросов
result_data = []  # Список для хранения данных о товарах
result_max_size = 5000  # Максимальное количество товаров в одном файле
result_prefix = 0  # Индекс файла при разбиении результатов

# URL API Wildberries
back_api_host = "https://catalog.wb.ru"

# Параметры запроса к API Wildberries
poepota = ("dest=-1255704&ab_testing=false&appType=1&curr=rub&hide_dtype=13&lang=ru&spp=30&uclusters=3&uiv=0&"
           "uv=AQEAAQIACSFPuZuvbEBouLo5vD2dMKq2sr-SMrcrK6fRO9O2H0MVOm28TDGWu6a1uMGtPo4_EDhlvnDBMkT3QTrEcrSZwp-"
           "9QsHsPVa9U727Qd-8E8H6vWoqaD5_O0hBNDzKtEc9bT6avqsv8D7bNeM_wkGGw6LAtD9VwbU_xD7dPlLA9sLSQs4xWMIdwmg8ljthQPO_"
           "U8LTQNKwtUJWsRU8kD0SLaU-RELIQOk9GcJxQWC_czclQquxtT1BrIC-LEBzoULCSMU_PKLEA0EKQcY8d0AwM-"
           "W5EMBIPWVAOkJGNLo4szdsPn1EFbuqLDu8J70bxZvAUD3HvAQzJkBtv1E5Mz8FxVE&sort=popular")


def write_result_file(result_data, result_prefix):
    """Функция записи данных в JSON-файл."""
    directory_path = "results_parse"  # Директория для сохранения файлов
    if not os.path.exists(directory_path):  # Проверяем, существует ли директория
        os.makedirs(directory_path)  # Создаем директорию, если её нет

    file_name = f"result_parse-{result_prefix}.json"  # Имя файла с индексом
    file_route = os.path.join(directory_path, file_name)  # Полный путь к файлу
    with open(file_route, 'w', encoding='utf-8') as file:  # Открываем файл на запись в кодировке utf-8
        json.dump(result_data, file, indent=4, ensure_ascii=False)  # Записываем JSON-данные с отступами


def get_main_catalog_children():
    """Функция получения подкатегорий каталога."""
    global request_count  # Используем глобальную переменную счетчика запросов
    session = Session()  # Создаем сессию requests
    session.mount('https://', HTTPAdapter(max_retries=retries))  # Настраиваем повторные попытки
    session.mount('http://', HTTPAdapter(max_retries=retries))

    try:
        request_count += 1  # Увеличиваем счетчик запросов
        catalog_response = session.get("https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json")
        catalog_response.raise_for_status()  # Проверяем статус ответа, если ошибка — вызываем исключение
    except Exception as e:
        logger.error(f"Ошибка: {e}")  # Логируем ошибку

    calalogs = json.loads(catalog_response.content)  # Загружаем JSON-данные

    main_calalog_childs = []  # Список подкатегорий
    for main_calalog in calalogs:
        main_clg_name = main_calalog.get("name")
        if main_clg_name == "Электроника":  # Фильтруем подкатегории только для "Электроники"
            main_calalog_childs = main_calalog.get("childs")  # Получаем список дочерних категорий
            break
    logger.info(f"success get catalog_childs")  # Логируем успешное получение данных
    return main_calalog_childs  # Возвращаем список подкатегорий


def get_products(list_catalog, page):
    """Функция сбора данных о товарах по категориям."""
    global request_count, result_prefix, result_data  # Используем глобальные переменные

    for main_calalog_child in list_catalog:

        query = main_calalog_child.get("query")  # Получаем параметры запроса
        name = main_calalog_child.get("name")  # Получаем имя категории
        shard = main_calalog_child.get("shard")  # Получаем ID раздела каталога

        logger.debug(f"Process with {name = }; {shard = } / {query = }")  # Логируем процесс обработки

        childs = main_calalog_child.get("childs", [])  # Получаем дочерние категории
        main_success = True  # Флаг успешного запроса
        while main_success:
            page += 1  # Увеличиваем номер страницы
            request_url = f"{back_api_host}/catalog/{shard}/v2/catalog?{query}&{page=}&{poepota}"  # Формируем URL запроса

            session = Session()  # Создаем новую сессию requests
            session.mount('https://', HTTPAdapter(max_retries=retries))  # Настраиваем повторные попытки
            session.mount('http://', HTTPAdapter(max_retries=retries))

            try:
                request_count += 1  # Увеличиваем счетчик запросов
                logger.info(f"GET: {request_url}")  # Логируем URL запроса
                response = session.get(request_url)  # Выполняем запрос
                response.raise_for_status()  # Проверяем статус ответа
            except Exception as e:
                logger.error(f"Ошибка: {e}")  # Логируем ошибку

            if response.status_code != 200:
                main_success = False  # Если статус не 200, останавливаем обработку
                logger.error(f"status = {response.status_code}, {response.reason}, {page = }, {response.url = }")
                continue

            if response.content:
                data = json.loads(response.content).get("data")  # Парсим JSON-ответ
                if data:
                    products = data.get("products", [])  # Получаем список товаров
                    for product in products:
                        results = {
                            "id": product.get("id"),
                            "brand": product.get("brand"),
                            "colors_name": [color.get("name") for color in product.get("colors", [])],
                            "name": product.get("name"),
                            "brand_id": product.get("brandId"),
                            "subject_id": product.get("subjectId"),
                            "supplier": product.get("supplier"),
                            "supplier_id": product.get("supplierId"),
                            "supplier_rating": product.get("supplierRating"),
                            "rating": product.get("rating"),
                            "review_rating": product.get("reviewRating"),
                            "nm_review_rating": product.get("nmReviewRating"),
                            "feedbacks": product.get("feedbacks"),
                            "total_quantity": product.get("totalQuantity"),
                            "basic": product.get("sizes", [{}])[0].get("price", {}).get("basic", "None"),
                            "product": product.get("sizes", [{}])[0].get("price", {}).get("product", "None"),
                            "total": product.get("sizes", [{}])[0].get("price", {}).get("total", "None"),
                            "logistics": product.get("sizes", [{}])[0].get("price", {}).get("logistics", "None"),
                        }
                        result_data.append(results)

                        if len(result_data) >= result_max_size:
                            write_result_file(result_data, result_prefix)
                            result_prefix += 1
                            result_data = []

        get_products(childs, 0)  # Рекурсивный вызов для дочерних категорий

main_catalog_child = get_main_catalog_children()
get_products(main_catalog_child, 0)
write_result_file(result_data, result_prefix)
logger.info(f"Final with {request_count = }")



