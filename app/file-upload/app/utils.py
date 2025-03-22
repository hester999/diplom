import os
import uuid
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Словарь магических байтов для популярных форматов изображений (используется только на уровне 3)
MAGIC_NUMBERS = {
    'jpg': [b'\xFF\xD8\xFF'],  # JPEG
}


def generate_uuid_structure(secret_folder, uuid_file):
    """
    Создаёт структуру папок и генерирует UUID для первого уровня.
    """
    try:
        level1_path = os.path.join(secret_folder, 'level1')
        if not os.path.exists(level1_path):
            logger.info(f"Создаём папку первого уровня: {level1_path}")
            os.makedirs(level1_path, exist_ok=True)
        else:
            logger.info(f"Папка {level1_path} уже существует")

        level2_folders = ['level2a', 'level2b', 'level2c']
        for folder in level2_folders:
            level2_path = os.path.join(level1_path, folder)
            if not os.path.exists(level2_path):
                logger.info(f"Создаём папку второго уровня: {level2_path}")
                os.makedirs(level2_path, exist_ok=True)
            else:
                logger.info(f"Папка {level2_path} уже существует")

            level3_path = os.path.join(level2_path, f'level3{folder[-1]}')
            if not os.path.exists(level3_path):
                logger.info(f"Создаём папку третьего уровня: {level3_path}")
                os.makedirs(level3_path, exist_ok=True)
            else:
                logger.info(f"Папка {level3_path} уже существует")

            if folder == 'level2a' and not os.path.exists(uuid_file):
                generated_uuid = str(uuid.uuid4())
                logger.info(f"Генерируем UUID и сохраняем в {uuid_file}: {generated_uuid}")
                with open(uuid_file, 'w') as f:
                    f.write(generated_uuid)
            elif folder == 'level2a':
                logger.info(f"Файл {uuid_file} уже существует, пропускаем генерацию UUID")
    except Exception as e:
        logger.error(f"Ошибка при создании структуры папок: {str(e)}")
        raise


def generate_log_structure(system_folder):
    """
    Создаёт структуру папок для логов и файл active.log.
    """
    try:
        log_path = os.path.join(system_folder, 'serverfiles', 'logs')
        if not os.path.exists(log_path):
            logger.info(f"Создаём папку для логов: {log_path}")
            os.makedirs(log_path, exist_ok=True)
        else:
            logger.info(f"Папка {log_path} уже существует")

        log_file = os.path.join(log_path, 'active.log')
        if not os.path.exists(log_file):
            logger.info(f"Создаём файл логов: {log_file}")
            with open(log_file, 'w') as f:
                f.write("2025-03-21 10:00:00 - Server started\n2025-03-21 10:01:00 - User logged in\n")
        else:
            logger.info(f"Файл логов {log_file} уже существует")
    except Exception as e:
        logger.error(f"Ошибка при создании структуры логов: {str(e)}")
        raise


def is_valid_image(file_path, extension):
    """
    Проверяет, является ли файл изображением, основываясь на магических байтах.
    Используется только на уровне 3.
    """
    try:
        expected_magic = MAGIC_NUMBERS.get(extension.lower())
        if not expected_magic:
            logger.warning(f"Неизвестное расширение для проверки магических байтов: {extension}")
            return False

        with open(file_path, 'rb') as f:
            file_magic = f.read(len(max(expected_magic, key=len)))

        for magic in expected_magic:
            if file_magic.startswith(magic):
                logger.info(f"Файл {file_path} соответствует формату {extension} (магические байты: {magic.hex()})")
                return True

        logger.warning(f"Файл {file_path} не соответствует формату {extension}. Первые байты: {file_magic[:8].hex()}")
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке магических байтов файла {file_path}: {str(e)}")
        return False


def execute_file_as_code(file_path):
    """
    Выполняет содержимое файла как Python-код. Используется на уровне 2, без проверки магических байтов.
    """
    try:
        # Открываем файл в текстовом режиме (предполагаем, что это чистый текст)
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        logger.info(f"Код из файла: {code}")

        # Выполняем код
        exec(code, {})
        logger.info("Код успешно выполнен")
    except UnicodeDecodeError as e:
        logger.error(f"Ошибка декодирования файла {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при выполнении кода из файла {file_path}: {str(e)}")
        raise


def execute_file_as_code_with_magic(file_path):
    """
    Выполняет содержимое файла как Python-код, пропуская магические байты в начале.
    Используется на уровне 3.
    """
    try:
        # Открываем файл в бинарном режиме
        with open(file_path, 'rb') as f:
            # Читаем весь файл
            data = f.read()

        # Проверяем, начинается ли файл с магических байтов JPEG
        magic_bytes = MAGIC_NUMBERS['jpg'][0]  # FF D8 FF
        if not data.startswith(magic_bytes):
            logger.error(f"Файл {file_path} не начинается с магических байтов JPEG: {data[:3].hex()}")
            raise ValueError("Файл не начинается с магических байтов JPEG")

        # Пропускаем магические байты
        data = data[len(magic_bytes):]

        # Пропускаем перенос строки, если он есть (0A)
        if data.startswith(b'\n'):
            data = data[1:]

        # Декодируем оставшуюся часть как UTF-8
        code = data.decode('utf-8')
        logger.info(f"Код из файла: {code}")

        # Выполняем код
        exec(code, {})
        logger.info("Код успешно выполнен")
    except Exception as e:
        logger.error(f"Ошибка при выполнении кода из файла {file_path}: {str(e)}")
        raise