import logging
import subprocess
from os.path import abspath, dirname, join, isfile
from random import randint
from time import sleep

from requests import get, exceptions

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(asctime)s: %(message)s\n')


def check_file(path) -> bool or dict:
    logging.info('Поиск токина бота и пароля администратора')
    if isfile(path):
        logging.info('Файл с токином бота и паролем администратора найден')
        logging.info('Проверка данных')
        with open(path, 'r') as file:
            data = {}
            for line in file.readlines():
                if '#' not in line:
                    d = line.replace('\'', '').replace('\n', '').split(' = ')
                    data.update({d[0]: d[1]})
        if (data.get('BOT_TOKEN')) and data.get('ADMIN_PSW'):
            ct = check_token(data["BOT_TOKEN"])
            if not ct:
                raise Exception('Что-то не так с токеном')
            logging.info(f'Пароль администратора: {data["ADMIN_PSW"]}')
            return True
        else:
            raise Exception('Отсутсвует токен или пароль администратора')
    else:
        logging.warning('Файл с данными не найден')
        return create_secret(path)
    return True


def check_token(token):
    logging.info('Проверка токена')
    try:
        page = get(f'https://api.telegram.org/bot{token}/getme')
    except exceptions.ConnectionError:
        raise Exception('Не удалось подключиться к серверу. Проверьте интернет соединение и VPN (proxy)')
    if page.status_code == 200:
        logging.info('Подключение к серверу и проверка токена прошли успешно')
    else:
        print(token)
        print('sadfas')
        raise Exception(f'Не верный токен бота ({token})')
    return True


def create_secret(path):
    logging.info('Генерация файла с данными')
    while True:
        sleep(1)
        token = input('Введите токен бота: ')
        if check_token(token):
            break
        sleep(1)
        print('Что бы отменить ввод и завершить приложение, введите Z')
        if token.lower() == 'z':
            raise Exception('Завершение приложения (отказ ввода токена)')

    psw = randint(10000, 99999)
    logging.info(f'Сгенерирован новый пароль администратора: {psw}')
    sleep(1)
    print('Если хотите изменить пароль, напишите его и нажмите enter')
    while True:
        sleep(1)
        pe = input('(Что бы оставить сгенерированый пароль, просто нажмите enter): ')
        print('pe1>>> ', pe)
        if ('\'' in pe) or ('\"' in pe) or ('\\' in pe):
            sleep(1)
            print('Пароль не должен содержать некоторые символы (\'\"\\), для отмены ввода отправте Z')
        elif pe.lower() == 'z':
            raise Exception('Завершение приложения (отказ ввода пароля')
        else:
            if pe:
                psw = pe
            break
    text = f'# Данные справа от знака равно (=) можно изменять. Данные должны быть заключены в кавычки и не ' \
           f'содержать их внутри себя.\n# Лучше просто удалите файл и перезапустите приложение, вам будет ' \
           f'предложено вписать данные\nBOT_TOKEN = \'{token}\'\nADMIN_PSW = \'{psw}\''
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)
    return True


def start_func():
    secret_file = join(abspath(dirname(__file__)), 'config', 'secret.py')
    status_file = check_file(secret_file)
    if status_file:
        while True:
            sleep(1)
            yn = input('Хотите изменить данные? (да/нет)')
            if 'д' in yn.lower():
                create_secret(secret_file)
                break
            if 'н' in yn.lower():
                break
    else:
        raise Exception('Отмена запуска')
    return True


def start():
    if start_func():
        logging.info('Старт бота')
        code = subprocess.call(['python', 'main.py'])
        print(code)
        if code != 0:
            raise Exception('Просмотрите логи. Что-то пошло не так при запуске приложения')
    else:
        raise Exception('Отмена запуска')


try:
    start()
except Exception:
    logging.exception('Отказ')
