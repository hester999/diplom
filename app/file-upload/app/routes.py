from flask import Blueprint, request, render_template, Response, redirect, url_for, session, send_file
import os
import logging
from utils import generate_uuid_structure, generate_log_structure, is_valid_image, execute_file_as_code, execute_file_as_code_with_magic

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_upload = Blueprint('file_upload', __name__, template_folder='../templates', static_folder='../static')
UPLOAD_FOLDER = '/app/static/uploads'
SECRET_FOLDER = '/app/secret'
SYSTEM_FOLDER = '/app/system'
UUID_FILE = os.path.join(SECRET_FOLDER, 'level1', 'level2a', 'level3a', 'uuid.txt')
LEVEL3_FLAG_FILE = os.path.join(SECRET_FOLDER, 'level3_flag.txt')
LOG_FOLDER = os.path.join(SYSTEM_FOLDER, 'serverfiles', 'logs')
LOG_FILE = os.path.join(LOG_FOLDER, 'active.log')

# Проверяем права доступа к корневой директории /app
try:
    if not os.access('/app', os.W_OK):
        logger.error("Нет прав на запись в /app")
    else:
        logger.info("Права на запись в /app есть")
except Exception as e:
    logger.error(f"Ошибка при проверке прав доступа к /app: {str(e)}")

# Создаём папку для загрузок, если её нет
try:
    if not os.path.exists(UPLOAD_FOLDER):
        logger.info(f"Создаём папку для загрузок: {UPLOAD_FOLDER}")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    else:
        logger.info(f"Папка {UPLOAD_FOLDER} уже существует")
except Exception as e:
    logger.error(f"Ошибка при создании папки {UPLOAD_FOLDER}: {str(e)}")

# Создаём папку /app/secret, если её нет, и устанавливаем права
try:
    if not os.path.exists(SECRET_FOLDER):
        logger.info(f"Создаём папку для секретных файлов: {SECRET_FOLDER}")
        os.makedirs(SECRET_FOLDER, exist_ok=True)
    else:
        logger.info(f"Папка {SECRET_FOLDER} уже существует")
    os.chmod(SECRET_FOLDER, 0o777)
    logger.info(f"Установлены права 777 на {SECRET_FOLDER}")
except Exception as e:
    logger.error(f"Ошибка при создании папки или установке прав на {SECRET_FOLDER}: {str(e)}")

# Создаём папку /app/system, если её нет, и устанавливаем права
try:
    if not os.path.exists(SYSTEM_FOLDER):
        logger.info(f"Создаём папку для системных файлов: {SYSTEM_FOLDER}")
        os.makedirs(SYSTEM_FOLDER, exist_ok=True)
    else:
        logger.info(f"Папка {SYSTEM_FOLDER} уже существует")
    os.chmod(SYSTEM_FOLDER, 0o777)
    logger.info(f"Установлены права 777 на {SYSTEM_FOLDER}")
except Exception as e:
    logger.error(f"Ошибка при создании папки или установке прав на {SYSTEM_FOLDER}: {str(e)}")

# Уровень 1: Загрузка файлов без проверки + вывод списка директорий
@file_upload.route('/file-upload/lvl1', methods=['GET', 'POST'])
def upload_file_lvl1():
    logger.info("Переход на /file-upload/lvl1, вызываем generate_uuid_structure()")
    try:
        generate_uuid_structure(SECRET_FOLDER, UUID_FILE)
    except Exception as e:
        logger.error(f"Ошибка при вызове generate_uuid_structure(): {str(e)}")
        return Response(f"Ошибка при создании структуры: {str(e)}", status=500)

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                logger.info(f"Сохраняем загруженный файл: {file_path}")
                try:
                    file.save(file_path)
                    session['file_uploaded'] = True
                    logger.info("Файл успешно загружен, флаг file_uploaded установлен в сессии")
                    return Response(
                        f"Файл {file.filename} загружен! Проверь <a href='/file-upload/lvl1/list_dir'>список директорий</a> или "
                        f"доступ к файлу: <a href='/file-upload/static/uploads/{file.filename}'>{file.filename}</a>",
                        status=200
                    )
                except Exception as e:
                    logger.error(f"Ошибка при сохранении файла {file_path}: {str(e)}")
                    return Response(f"Ошибка при сохранении файла: {str(e)}", status=500)
        elif 'password' in request.form:
            user_password = request.form.get('password')
            try:
                with open(UUID_FILE, 'r') as f:
                    correct_password = f.read().strip()
                logger.info(f"Проверяем пароль: введённый={user_password}, правильный={correct_password}")
                if user_password == correct_password:
                    logger.info("Пароль верный, перенаправляем на Уровень 2")
                    return redirect(url_for('file_upload.upload_file_lvl2'))
                else:
                    logger.info("Пароль неверный")
                    return Response("Неверный пароль! Попробуй снова.", status=401)
            except FileNotFoundError:
                logger.error(f"Файл с паролем не найден: {UUID_FILE}")
                return Response("Файл с паролем не найден. Попробуй снова позже.", status=500)
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {UUID_FILE}: {str(e)}")
                return Response(f"Ошибка: {str(e)}", status=500)

    return render_template('lvl1.html')

# Эндпоинт для вывода списка директорий
@file_upload.route('/file-upload/lvl1/list_dir', methods=['GET'])
def list_dir_lvl1():
    if not session.get('file_uploaded'):
        logger.warning("Попытка доступа к /file-upload/lvl1/list_dir без загрузки файла")
        return Response("Сначала загрузите файл, чтобы получить доступ к списку директорий!", status=403)

    dir_path = request.args.get('path', UPLOAD_FOLDER)
    logger.info(f"Запрос списка директорий: {dir_path}")
    try:
        files = os.listdir(dir_path)
        return Response("<br>".join(files), status=200)
    except Exception as e:
        logger.error(f"Ошибка при получении списка директорий: {str(e)}")
        return Response(f"Ошибка: {str(e)}", status=400)

# Эндпоинт для чтения содержимого файлов через форму
@file_upload.route('/file-upload/lvl1/read_file', methods=['GET', 'POST'])
def read_file_lvl1():
    if not session.get('file_uploaded'):
        logger.warning("Попытка доступа к /file-upload/lvl1/read_file без загрузки файла")
        return Response("Сначала загрузите файл, чтобы получить доступ к чтению файлов!", status=403)

    if request.method == 'POST':
        file_path = request.form.get('path')
        if not file_path:
            logger.warning("Параметр 'path' не указан в форме")
            return render_template('read_file.html', error="Параметр 'path' обязателен!")

        logger.info(f"Запрос на чтение файла: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return render_template('read_file.html', content=content)
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")
            return render_template('read_file.html', error=f"Ошибка: {str(e)}")

    return render_template('read_file.html')

# Уровень 2: Обход защиты загрузки файлов (без магических байтов)
@file_upload.route('/file-upload/lvl2', methods=['GET', 'POST'])
def upload_file_lvl2():
    logger.info("Переход на /file-upload/lvl2")

    schema_access_file = os.path.join(SECRET_FOLDER, 'schema_access.txt')
    schema_access = False
    logger.info(f"Проверяем наличие файла: {schema_access_file}")
    if os.path.exists(schema_access_file):
        logger.info(f"Файл {schema_access_file} существует")
        try:
            with open(schema_access_file, 'r') as f:
                content = f.read().strip()
            logger.info(f"Содержимое файла {schema_access_file}: '{content}' (длина: {len(content)})")
            if content == 'access_granted':
                schema_access = True
                logger.info("Файл schema_access.txt найден с правильным содержимым, доступ к схеме предоставлен")
            else:
                logger.info(f"Файл schema_access.txt найден, но содержимое неверное: '{content}' != 'access_granted'")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {schema_access_file}: {str(e)}")
    else:
        logger.info(f"Файл {schema_access_file} не существует")

    if request.method == 'POST':
        if 'file' not in request.files:
            logger.warning("Файл не выбран в форме загрузки")
            return render_template('lvl2.html', error='Файл не выбран.', schema_access=schema_access)

        file = request.files['file']

        if file.filename == '':
            logger.warning("Файл не выбран в форме загрузки")
            return render_template('lvl2.html', error='Файл не выбран.', schema_access=schema_access)

        if not (file.filename.endswith('.txt') or file.filename.endswith('.jpg')):
            logger.warning(f"Попытка загрузки файла с недопустимым расширением: {file.filename}")
            return render_template('lvl2.html', error='Разрешены только файлы с расширениями .txt и .jpg.',
                                   schema_access=schema_access)

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        logger.info(f"Сохраняем загруженный файл: {file_path}")
        try:
            file.save(file_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {file_path}: {str(e)}")
            return render_template('lvl2.html', error=f'Ошибка при сохранении файла: {str(e)}',
                                   schema_access=schema_access)

        if not os.path.exists(file_path):
            logger.error(f"Файл {file_path} не найден после сохранения")
            return render_template('lvl2.html', error=f'Файл {file_path} не найден после сохранения.',
                                   schema_access=schema_access)

        logger.info(f"Читаем и выполняем содержимое файла: {file_path}")
        try:
            # Используем функцию без проверки магических байтов
            execute_file_as_code(file_path)
            if os.path.exists(schema_access_file):
                logger.info(f"Файл {schema_access_file} существует после выполнения кода")
                try:
                    with open(schema_access_file, 'r') as f:
                        content = f.read().strip()
                    logger.info(f"Содержимое файла {schema_access_file}: '{content}' (длина: {len(content)})")
                    if content == 'access_granted':
                        schema_access = True
                        logger.info("Файл schema_access.txt создан с правильным содержимым после выполнения кода")
                    else:
                        logger.info(f"Содержимое файла {schema_access_file} неверное: '{content}' != 'access_granted'")
                except Exception as e:
                    logger.error(f"Ошибка при чтении файла {schema_access_file} после выполнения кода: {str(e)}")
            else:
                logger.warning(f"Файл {schema_access_file} не был создан после выполнения кода")
            logger.info(f"После выполнения кода schema_access={schema_access}")
            return render_template('lvl2.html', message='Файл обработан.', schema_access=schema_access)
        except Exception as e:
            logger.error(f"Ошибка при выполнении кода из файла {file_path}: {str(e)}")
            return render_template('lvl2.html', error=f'Ошибка при выполнении кода: {str(e)}',
                                   schema_access=schema_access)

    if not schema_access and os.path.exists(schema_access_file):
        logger.info("Повторная проверка перед рендерингом шаблона")
        try:
            with open(schema_access_file, 'r') as f:
                content = f.read().strip()
            logger.info(f"Содержимое файла {schema_access_file} при повторной проверке: '{content}'")
            if content == 'access_granted':
                schema_access = True
                logger.info("Повторная проверка: schema_access установлен в True")
        except Exception as e:
            logger.error(f"Ошибка при повторной проверке файла {schema_access_file}: {str(e)}")

    logger.info(f"Перед рендерингом шаблона schema_access={schema_access}")
    return render_template('lvl2.html', schema_access=schema_access)

# Маршрут для скачивания схемы
@file_upload.route('/file-upload/lvl2/download_schema', methods=['GET'])
def download_schema():
    logger.info("Запрос на скачивание схемы базы данных")
    schema_access_file = os.path.join(SECRET_FOLDER, 'schema_access.txt')
    if not os.path.exists(schema_access_file):
        logger.warning("Файл schema_access.txt не найден, доступ к схеме не предоставлен")
        return render_template('lvl2.html', error='Доступ к схеме не получен. Выполни задание.')

    try:
        with open(schema_access_file, 'r') as f:
            content = f.read().strip()
        if content != 'access_granted':
            logger.warning("Файл schema_access.txt найден, но содержимое неверное")
            return render_template('lvl2.html', error='Доступ к схеме не получен. Выполни задание.')
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {schema_access_file}: {str(e)}")
        return render_template('lvl2.html', error=f'Ошибка при чтении файла: {str(e)}')

    schema_path = os.path.join(file_upload.static_folder, 'images', 'schema.png')
    if not os.path.exists(schema_path):
        logger.error(f"Файл схемы не найден: {schema_path}")
        return render_template('lvl2.html', error='Файл схемы не найден на сервере.')

    logger.info(f"Отправляем файл схемы: {schema_path}")
    return send_file(schema_path, as_attachment=True)

# Уровень 3: Удаление файла логов с помощью замаскированного кода и Path Traversal
@file_upload.route('/file-upload/lvl3', methods=['GET', 'POST'])
def upload_file_lvl3():
    logger.info("Переход на /file-upload/lvl3")

    # Создаём структуру папок для логов
    try:
        generate_log_structure(SYSTEM_FOLDER)
    except Exception as e:
        logger.error(f"Ошибка при создании структуры логов: {str(e)}")
        return Response(f"Ошибка при создании структуры логов: {str(e)}", status=500)

    # Проверяем, выполнен ли уровень (файл active.log удалён, и в папке остался только один .jpg файл)
    level3_completed = False
    if not os.path.exists(LOG_FILE):
        try:
            files_in_log_folder = os.listdir(LOG_FOLDER)
            jpg_files = [f for f in files_in_log_folder if f.endswith('.jpg')]
            if len(files_in_log_folder) == 1 and len(jpg_files) == 1:
                level3_completed = True
                logger.info("Уровень 3 пройден: active.log удалён, в папке остался только один .jpg файл")
            else:
                logger.info(f"Уровень 3 не пройден: в папке {LOG_FOLDER} находятся файлы: {files_in_log_folder}")
        except Exception as e:
            logger.error(f"Ошибка при проверке содержимого папки {LOG_FOLDER}: {str(e)}")

    if request.method == 'POST':
        if 'file' not in request.files:
            logger.warning("Файл не выбран в форме загрузки")
            return render_template('lvl3.html', error='Файл не выбран.', level3_completed=level3_completed)

        file = request.files['file']
        if file.filename == '':
            logger.warning("Файл не выбран в форме загрузки")
            return render_template('lvl3.html', error='Файл не выбран.', level3_completed=level3_completed)

        # Разрешены только файлы .jpg
        if not file.filename.endswith('.jpg'):
            logger.warning(f"Попытка загрузки файла с недопустимым расширением: {file.filename}")
            return render_template('lvl3.html', error='Разрешены только файлы с расширением .jpg.',
                                   level3_completed=level3_completed)

        # Уязвимость Path Traversal: получаем имя файла из формы
        save_filename = request.form.get('filename', file.filename)
        # Уязвимость: не очищаем путь, что позволяет Path Traversal
        # Базовый путь — /app/static/uploads, от него пользователь может использовать ../
        save_path = os.path.join(UPLOAD_FOLDER, save_filename)
        logger.info(f"Сохраняем файл по пути: {save_path}")

        # Убедимся, что директория существует
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir, exist_ok=True)
                logger.info(f"Создана директория для сохранения файла: {save_dir}")
            except Exception as e:
                logger.error(f"Ошибка при создании директории {save_dir}: {str(e)}")
                return render_template('lvl3.html', error=f'Ошибка при создании директории: {str(e)}',
                                       level3_completed=level3_completed)

        # Сохраняем файл (уязвимость Path Traversal)
        try:
            file.save(save_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {save_path}: {str(e)}")
            return render_template('lvl3.html', error=f'Ошибка при сохранении файла: {str(e)}',
                                   level3_completed=level3_completed)

        if not os.path.exists(save_path):
            logger.error(f"Файл {save_path} не найден после сохранения")
            return render_template('lvl3.html', error=f'Файл {save_path} не найден после сохранения.',
                                   level3_completed=level3_completed)

        # Проверяем, что файл сохранён в папке /app/system/serverfiles/logs/
        if not os.path.abspath(save_path).startswith(os.path.abspath(LOG_FOLDER)):
            logger.warning(f"Файл {save_path} сохранён не в папке логов {LOG_FOLDER}")
            return render_template('lvl3.html', error=f'Файл должен быть сохранён в папке {LOG_FOLDER}. Используй Path Traversal.',
                                   level3_completed=level3_completed)

        # Проверяем магические байты
        if not is_valid_image(save_path, 'jpg'):
            logger.warning(f"Файл {save_filename} не является валидным изображением JPEG")
            return render_template('lvl3.html', error='Файл должен быть валидным изображением JPEG (по магическим байтам).',
                                   level3_completed=level3_completed)

        # Выполняем код из файла (с проверкой магических байтов)
        try:
            execute_file_as_code_with_magic(save_path)
            # Проверяем, удалён ли active.log и остался ли только один .jpg файл
            if not os.path.exists(LOG_FILE):
                files_in_log_folder = os.listdir(LOG_FOLDER)
                jpg_files = [f for f in files_in_log_folder if f.endswith('.jpg')]
                if len(files_in_log_folder) == 1 and len(jpg_files) == 1:
                    level3_completed = True
                    logger.info("Уровень 3 пройден после выполнения кода")
                else:
                    logger.info(f"Уровень 3 не пройден после выполнения кода: в папке {LOG_FOLDER} находятся файлы: {files_in_log_folder}")
            return render_template('lvl3.html', message='Файл обработан.', level3_completed=level3_completed)
        except Exception as e:
            logger.error(f"Ошибка при выполнении кода из файла {save_path}: {str(e)}")
            return render_template('lvl3.html', error=f'Ошибка при выполнении кода: {str(e)}',
                                   level3_completed=level3_completed)

    return render_template('lvl3.html', level3_completed=level3_completed)