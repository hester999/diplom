from flask import Blueprint, request, render_template, Response, redirect, url_for, session, send_file
import os
import logging
import subprocess
import urllib.parse
from apscheduler.schedulers.background import BackgroundScheduler
import utils

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
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.chmod(UPLOAD_FOLDER, 0o777)
except Exception as e:
    logger.error(f"Ошибка при создании папки {UPLOAD_FOLDER}: {str(e)}")

# Создаём папку /app/secret, если её нет, и устанавливаем права
try:
    if not os.path.exists(SECRET_FOLDER):
        os.makedirs(SECRET_FOLDER, exist_ok=True)
    os.chmod(SECRET_FOLDER, 0o777)
except Exception as e:
    logger.error(f"Ошибка при создании папки или установке прав на {SECRET_FOLDER}: {str(e)}")

# Создаём папку /app/system, если её нет, и устанавливаем права
try:
    if not os.path.exists(SYSTEM_FOLDER):
        os.makedirs(SYSTEM_FOLDER, exist_ok=True)
    os.chmod(SYSTEM_FOLDER, 0o777)
except Exception as e:
    logger.error(f"Ошибка при создании папки или установке прав на {SYSTEM_FOLDER}: {str(e)}")

# Функция для проверки и выполнения .py файлов
def check_and_execute_py_files():
    try:
        if not os.access(UPLOAD_FOLDER, os.R_OK):
            logger.error(f"Нет прав на чтение директории {UPLOAD_FOLDER}")
            return
        files = os.listdir(UPLOAD_FOLDER)
        for filename in files:
            if filename.endswith('.py'):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if not os.access(file_path, os.R_OK | os.X_OK):
                    logger.error(f"Нет прав на чтение или выполнение файла {file_path}")
                    continue
                try:
                    result = subprocess.run(['python3', file_path], capture_output=True, text=True)
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Ошибка при выполнении файла {file_path}: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка в фоновом процессе: {str(e)}")

# Инициализируем планировщик
scheduler = BackgroundScheduler()
scheduler.add_job(check_and_execute_py_files, 'interval', seconds=30)
scheduler.start()

# Уровень 1: Загрузка файлов без проверки + вывод списка директорий
@file_upload.route('/file-upload/lvl1', methods=['GET', 'POST'])
def upload_file_lvl1():
    try:
        utils.generate_uuid_structure(SECRET_FOLDER, UUID_FILE)
    except Exception as e:
        logger.error(f"Ошибка при вызове generate_uuid_structure(): {str(e)}")
        return Response(f"Ошибка при создании структуры: {str(e)}", status=500)

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                try:
                    file.save(file_path)
                    session['file_uploaded'] = True
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
                if user_password == correct_password:
                    return redirect(url_for('file_upload.upload_file_lvl2'))
                else:
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
        return Response("Сначала загрузите файл, чтобы получить доступ к списку директорий!", status=403)

    dir_path = request.args.get('path', UPLOAD_FOLDER)
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
        return Response("Сначала загрузите файл, чтобы получить доступ к чтению файлов!", status=403)

    if request.method == 'POST':
        file_path = request.form.get('path')
        if not file_path:
            return render_template('read_file.html', error="Параметр 'path' обязателен!")

        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return render_template('read_file.html', content=content)
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")
            return render_template('read_file.html', error=f"Ошибка: {str(e)}")

    return render_template('read_file.html')

# Уровень 2: Обход проверки расширения для выполнения Python-скрипта
@file_upload.route('/file-upload/lvl2', methods=['GET', 'POST'])
def upload_file_lvl2():
    schema_access_file = os.path.join(SECRET_FOLDER, 'schema_access.txt')
    schema_access = False
    if os.path.exists(schema_access_file):
        try:
            with open(schema_access_file, 'r') as f:
                content = f.read().strip()
            if content == 'access_granted':
                schema_access = True
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {schema_access_file}: {str(e)}")

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('lvl2.html', error='Файл не выбран.', schema_access=schema_access)

        file = request.files['file']

        if file.filename == '':
            return render_template('lvl2.html', error='Файл не выбран.', schema_access=schema_access)

        # Проверяем расширение (уязвимая проверка, допускающая обход)
        if not (file.filename.lower().endswith('.jpg') or file.filename.lower().endswith('.png')):
            return render_template('lvl2.html', error='Разрешены только файлы с расширениями .jpg и .png.',
                                   schema_access=schema_access)

        # Декодируем имя файла, чтобы обработать %00 как null-byte
        decoded_filename = urllib.parse.unquote(file.filename)
        # Явно заменяем %00 на \0, если он присутствует
        if '%00' in decoded_filename:
            decoded_filename = decoded_filename.replace('%00', '\0')
        # Обрабатываем null-byte: обрезаем всё после \0
        if '\0' in decoded_filename:
            filename = decoded_filename.split('\0')[0]
        # Проверяем двойное расширение (например, exploit.py.jpg)
        elif '.py.' in decoded_filename:
            py_index = decoded_filename.rfind('.py')
            filename = decoded_filename[:py_index + 3]
        else:
            filename = decoded_filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Сохраняем файл
        try:
            file.save(file_path)
            os.chmod(file_path, 0o777)
            return render_template('lvl2.html', message='Файл загружен. Фоновый процесс выполнит .py файлы в течение 30 секунд. Обновите страницу, чтобы проверить результат.',
                                   schema_access=schema_access)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {file_path}: {str(e)}")
            return render_template('lvl2.html', error=f'Ошибка при сохранении файла: {str(e)}',
                                   schema_access=schema_access)

    if not schema_access and os.path.exists(schema_access_file):
        try:
            with open(schema_access_file, 'r') as f:
                content = f.read().strip()
            if content == 'access_granted':
                schema_access = True
        except Exception as e:
            logger.error(f"Ошибка при повторной проверке файла {schema_access_file}: {str(e)}")

    return render_template('lvl2.html', schema_access=schema_access)

# Маршрут для скачивания схемы
@file_upload.route('/file-upload/lvl2/download_schema', methods=['GET'])
def download_schema():
    schema_access_file = os.path.join(SECRET_FOLDER, 'schema_access.txt')
    if not os.path.exists(schema_access_file):
        return render_template('lvl2.html', error='Доступ к схеме не получен. Выполни задание.')

    try:
        with open(schema_access_file, 'r') as f:
            content = f.read().strip()
        if content != 'access_granted':
            return render_template('lvl2.html', error='Доступ к схеме не получен. Выполни задание.')
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {schema_access_file}: {str(e)}")
        return render_template('lvl2.html', error=f'Ошибка при чтении файла: {str(e)}')

    schema_path = os.path.join(file_upload.static_folder, 'images', 'schema.png')
    if not os.path.exists(schema_path):
        logger.error(f"Файл схемы не найден: {schema_path}")
        return render_template('lvl2.html', error='Файл схемы не найден на сервере.')

    return send_file(schema_path, as_attachment=True)

# Уровень 3: Удаление файла логов с помощью замаскированного кода и Path Traversal
@file_upload.route('/file-upload/lvl3', methods=['GET', 'POST'])
def upload_file_lvl3():
    if request.method == 'GET':
        try:
            utils.generate_log_structure(SYSTEM_FOLDER)
        except Exception as e:
            logger.error(f"Ошибка при создании структуры логов: {str(e)}")
            return Response(f"Ошибка при создании структуры логов: {str(e)}", status=500)

    level3_completed = False
    if not os.path.exists(LOG_FILE):
        try:
            files_in_log_folder = os.listdir(LOG_FOLDER)
            jpg_files = [f for f in files_in_log_folder if f.endswith('.jpg')]
            if len(files_in_log_folder) == 1 and len(jpg_files) == 1:
                level3_completed = True
        except Exception as e:
            logger.error(f"Ошибка при проверке содержимого папки {LOG_FOLDER}: {str(e)}")

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('lvl3.html', error='Файл не выбран.', level3_completed=level3_completed)

        file = request.files['file']
        if file.filename == '':
            return render_template('lvl3.html', error='Файл не выбран.', level3_completed=level3_completed)

        if not file.filename.lower().endswith('.jpg'):
            return render_template('lvl3.html', error='Разрешены только файлы с расширением .jpg.',
                                   level3_completed=level3_completed)

        save_filename = request.form.get('filename')
        if save_filename:
            pass
        else:
            save_filename = file.filename

        save_path = os.path.join(UPLOAD_FOLDER, save_filename)

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Ошибка при создании директории {save_dir}: {str(e)}")
                return render_template('lvl3.html', error=f'Ошибка при создании директории: {str(e)}',
                                       level3_completed=level3_completed)

        try:
            file.save(save_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {save_path}: {str(e)}")
            return render_template('lvl3.html', error=f'Ошибка при сохранении файла: {str(e)}',
                                   level3_completed=level3_completed)

        if not os.path.exists(save_path):
            return render_template('lvl3.html', error=f'Файл {save_path} не найден после сохранения.',
                                   level3_completed=level3_completed)

        if not os.path.abspath(save_path).startswith(os.path.abspath(LOG_FOLDER)):
            return render_template('lvl3.html', error=f'Файл должен быть сохранён в папке {LOG_FOLDER}. Используй Path Traversal в имени файла или в поле "Имя файла для сохранения".',
                                   level3_completed=level3_completed)

        if not utils.is_valid_image(save_path, 'jpg'):
            return render_template('lvl3.html', error='Файл должен быть валидным изображением JPEG (по магическим байтам).',
                                   level3_completed=level3_completed)

        try:
            utils.execute_file_as_code_with_magic(save_path)
            if not os.path.exists(LOG_FILE):
                files_in_log_folder = os.listdir(LOG_FOLDER)
                jpg_files = [f for f in files_in_log_folder if f.endswith('.jpg')]
                if len(files_in_log_folder) == 1 and len(jpg_files) == 1:
                    level3_completed = True
            return render_template('lvl3.html', message='Файл обработан.', level3_completed=level3_completed)
        except Exception as e:
            logger.error(f"Ошибка при выполнении кода из файла {save_path}: {str(e)}")
            return render_template('lvl3.html', error=f'Ошибка при выполнении кода: {str(e)}',
                                   level3_completed=level3_completed)

    return render_template('lvl3.html', level3_completed=level3_completed)