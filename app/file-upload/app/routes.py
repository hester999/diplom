from flask import Blueprint, request, render_template, Response, redirect, url_for, session, send_file
import os
import uuid
import logging
import subprocess

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_upload = Blueprint('file_upload', __name__, template_folder='../templates', static_folder='../static')
UPLOAD_FOLDER = '/app/static/uploads'
SECRET_FOLDER = '/app/secret'
UUID_FILE = os.path.join(SECRET_FOLDER, 'level1', 'level2a', 'level3a', 'uuid.txt')

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

# Создаём папку /app/secret, если её нет
try:
    if not os.path.exists(SECRET_FOLDER):
        logger.info(f"Создаём папку для секретных файлов: {SECRET_FOLDER}")
        os.makedirs(SECRET_FOLDER, exist_ok=True)
    else:
        logger.info(f"Папка {SECRET_FOLDER} уже существует")
except Exception as e:
    logger.error(f"Ошибка при создании папки {SECRET_FOLDER}: {str(e)}")


# Функция для создания структуры папок и генерации UUID
def generate_uuid_structure():
    try:
        # Путь к первому уровню
        level1_path = os.path.join(SECRET_FOLDER, 'level1')
        if not os.path.exists(level1_path):
            logger.info(f"Создаём папку первого уровня: {level1_path}")
            os.makedirs(level1_path, exist_ok=True)
        else:
            logger.info(f"Папка {level1_path} уже существует")

        # Создаём папки второго уровня (level2a, level2b, level2c)
        level2_folders = ['level2a', 'level2b', 'level2c']
        for folder in level2_folders:
            level2_path = os.path.join(level1_path, folder)
            if not os.path.exists(level2_path):
                logger.info(f"Создаём папку второго уровня: {level2_path}")
                os.makedirs(level2_path, exist_ok=True)
            else:
                logger.info(f"Папка {level2_path} уже существует")

            # Создаём папки третьего уровня (level3a, level3b, level3c)
            level3_path = os.path.join(level2_path, f'level3{folder[-1]}')  # level3a, level3b, level3c
            if not os.path.exists(level3_path):
                logger.info(f"Создаём папку третьего уровня: {level3_path}")
                os.makedirs(level3_path, exist_ok=True)
            else:
                logger.info(f"Папка {level3_path} уже существует")

            # Генерируем UUID и сохраняем его в файл только в level3a, если файла ещё нет
            if folder == 'level2a' and not os.path.exists(UUID_FILE):
                generated_uuid = str(uuid.uuid4())  # Генерируем UUID
                logger.info(f"Генерируем UUID и сохраняем в {UUID_FILE}: {generated_uuid}")
                with open(UUID_FILE, 'w') as f:
                    f.write(generated_uuid)
            elif folder == 'level2a':
                logger.info(f"Файл {UUID_FILE} уже существует, пропускаем генерацию UUID")
    except Exception as e:
        logger.error(f"Ошибка при создании структуры папок: {str(e)}")
        raise


# Уровень 1: Загрузка файлов без проверки + вывод списка директорий
@file_upload.route('/file-upload/lvl1', methods=['GET', 'POST'])
def upload_file_lvl1():
    # Вызываем функцию для создания структуры и генерации UUID
    logger.info("Переход на /file-upload/lvl1, вызываем generate_uuid_structure()")
    try:
        generate_uuid_structure()
    except Exception as e:
        logger.error(f"Ошибка при вызове generate_uuid_structure(): {str(e)}")
        return Response(f"Ошибка при создании структуры: {str(e)}", status=500)

    if request.method == 'POST':
        # Проверяем, является ли запрос загрузкой файла
        if 'file' in request.files:
            file = request.files['file']
            if file:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                logger.info(f"Сохраняем загруженный файл: {file_path}")
                try:
                    file.save(file_path)
                    # Устанавливаем флаг в сессии, что файл загружен
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
        # Проверяем, является ли запрос проверкой пароля
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
    # Проверяем, загружал ли пользователь файл
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
    # Проверяем, загружал ли пользователь файл
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

    # Если GET-запрос, показываем форму
    return render_template('read_file.html')


# Уровень 2: Обход защиты загрузки файлов
@file_upload.route('/file-upload/lvl2', methods=['GET', 'POST'])
def upload_file_lvl2():
    logger.info("Переход на /file-upload/lvl2")

    # Проверяем, создан ли файл для доступа к схеме
    schema_access_file = os.path.join(SECRET_FOLDER, 'schema_access.txt')
    schema_access = False
    logger.info(f"Проверяем наличие файла: {schema_access_file}")
    if os.path.exists(schema_access_file):
        try:
            with open(schema_access_file, 'r') as f:
                content = f.read().strip()
            logger.info(f"Содержимое файла {schema_access_file}: '{content}' (длина: {len(content)})")
            if content == 'access_granted':
                schema_access = True
                logger.info("Файл schema_access.txt найден с правильным содержимым, доступ к схеме предоставлен")
            else:
                logger.info("Файл schema_access.txt найден, но содержимое неверное")
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {schema_access_file}: {str(e)}")

    if request.method == 'POST':
        # Проверяем, есть ли файл в запросе
        if 'file' not in request.files:
            logger.warning("Файл не выбран в форме загрузки")
            return render_template('lvl2.html', error='Файл не выбран.', schema_access=schema_access)

        file = request.files['file']

        # Проверяем, что файл выбран
        if file.filename == '':
            logger.warning("Файл не выбран в форме загрузки")
            return render_template('lvl2.html', error='Файл не выбран.', schema_access=schema_access)

        # Проверяем расширение файла (защита, которую нужно обойти)
        if not (file.filename.endswith('.txt') or file.filename.endswith('.jpg')):
            logger.warning(f"Попытка загрузки файла с недопустимым расширением: {file.filename}")
            return render_template('lvl2.html', error='Разрешены только файлы с расширениями .txt и .jpg.',
                                   schema_access=schema_access)

        # Сохраняем файл
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        logger.info(f"Сохраняем загруженный файл: {file_path}")
        try:
            file.save(file_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {file_path}: {str(e)}")
            return render_template('lvl2.html', error=f'Ошибка при сохранении файла: {str(e)}',
                                   schema_access=schema_access)

        # Проверяем, существует ли файл перед выполнением
        if not os.path.exists(file_path):
            logger.error(f"Файл {file_path} не найден после сохранения")
            return render_template('lvl2.html', error=f'Файл {file_path} не найден после сохранения.',
                                   schema_access=schema_access)

        # Уязвимость: читаем содержимое файла и выполняем его как Python-код
        logger.info(f"Читаем и выполняем содержимое файла: {file_path}")
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            logger.info(f"Код из файла: {code}")
            # Выполняем код с помощью exec()
            exec(code, {})
            logger.info("Код успешно выполнен")

            # После выполнения кода проверяем файл schema_access.txt заново
            if os.path.exists(schema_access_file):
                with open(schema_access_file, 'r') as f:
                    content = f.read().strip()
                logger.info(f"После выполнения кода: содержимое файла {schema_access_file}: '{content}'")
                if content == 'access_granted':
                    schema_access = True
                    logger.info("Файл schema_access.txt создан с правильным содержимым после выполнения кода")
                else:
                    logger.info(f"После выполнения кода: содержимое файла неверное: '{content}' != 'access_granted'")
            else:
                logger.warning(f"Файл {schema_access_file} не был создан после выполнения кода")

            logger.info(f"После выполнения кода schema_access={schema_access}")
            return render_template('lvl2.html', message='Файл обработан.', schema_access=schema_access)
        except Exception as e:
            logger.error(f"Ошибка при выполнении кода из файла {file_path}: {str(e)}")
            return render_template('lvl2.html', error=f'Ошибка при выполнении кода: {str(e)}',
                                   schema_access=schema_access)

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


# Уровень 3 (заглушка)
@file_upload.route('/file-upload/lvl3', methods=['GET', 'POST'])
def upload_file_lvl3():
    logger.info("Переход на /file-upload/lvl3")
    return "Поздравляем! Ты на уровне 3!"