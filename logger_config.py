import logging
import os

import datetime

# Получаем текущую дату и время по Москве
current_time = datetime.datetime.now().strftime("%d.%m.%Y_%H.%M")

# Создаем имя файла с датой и временем
log_filename = f"{current_time}_wb_parse.log"

# Создаём директорию для логов, если её нет
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Настраиваем логирование
logging.basicConfig(
    filename=os.path.join(log_directory, log_filename),  # Файл логов
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщения
    datefmt='%Y-%m-%d %H:%M:%S',  # Формат даты
    encoding='utf-8'  # Кодировка для поддержки кириллицы
)

# Создаём объект логгера
logger = logging.getLogger(__name__)