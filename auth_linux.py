#!/usr/bin/python3

import re
import logging
import os
import getpass


logging.basicConfig(
                    level=logging.DEBUG, filename='/var/log/auth_script.log',
                    format='%(asctime)s : %(levelname)s : %(name)s => %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    )
logger = logging.getLogger(__name__)


USERNAME = getpass.getuser()
os.chdir('/etc/freeradius/3.0/mods-config/files')
pwd = os.getcwd()
INPUT_FILE = 'authorize'
OUTPUT_FILE = 'authorize'


# text_color просто разукрашивает текст.
class TextColor:
    Red = '\033[91m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    END = '\033[0m'


# input_data() принимает и проверяет правильность входящих данных
def input_data():
    try:
        welcome = 'Пожалуйста, введите значения от 1 до 24 через запятую или одно число.\n' \
                  + 'Пример: 1,2,3 или 24 или 4 5 6 или любой другой символ в качестве разделителя.'
        print(welcome)
        outlets_input = input()
        logging.debug('Получение данных... Вывод: %s', outlets_input)
        splitting_outlets = re.split(r"\D+", outlets_input)
        logging.debug('Преобразование строки в список... Вывод: %s', splitting_outlets)
        space = ''
        while space in splitting_outlets:
            splitting_outlets.remove('')
            logging.debug('Удаление пустых объектов... Вывод: %s', splitting_outlets)
            if len(splitting_outlets) == 0:
                bad_input = '   Вы ничего не ввели! Пожалуйста, запустите программу заново.'
                logging.error('Пустой ввод!')
                logging.info('Прерывание работы скрипта.')
                raise SystemExit(TextColor.Red + str(splitting_outlets) + bad_input + TextColor.END)
        transform_outlets = list(set(map(int, splitting_outlets)))
        logging.debug('Преобразование списка в числа... Вывод: %s', transform_outlets)
        transform_outlets.sort()
        logging.debug('Сортировка списка... Вывод: %s', transform_outlets)
        if 1 <= min(transform_outlets) and max(transform_outlets) <= 24:
            outlets = ','.join(str(e) for e in transform_outlets)
            logging.debug('Преобразование данных для записи... Вывод: %s', outlets)
            return outlets
        else:
            bad_data = '   Введённые данные отличаются от требуемых. ' \
                       'Пожалуйста, запустите программу заново и введите число от 1 до 24.'
            logging.error('Введённые данные отличаются от требуемых! ')
            logging.info('Прерывание работы скрипта.')
            raise SystemExit(TextColor.Red + str(transform_outlets) + bad_data + TextColor.END)
    except Exception as e:
        logging.warning(e)


# check_username() проверка пользователя
def check_username():
    try:
        with open(INPUT_FILE, "r") as data:
            username = USERNAME
            logger.debug('Чтение пользователя ' + username + '...')
            text = data.read()
            logging.debug('Поиск пользователя в файле...')
            if username in text:
                logging.debug('Пользователь ' + username + ' найден!')
                return True
            else:
                logging.error('Пользователя с таким именем не существует!')
                logging.info('Прерывание работы скрипта.')
                raise SystemExit(TextColor.Red + 'Пользователя с таким именем не существует!\n'
                                                 'Пожалуйста, свяжитесь с системным администратором.' + TextColor.END)
    except Exception as e:
        logging.warning(e)


# modification_data() заменяет текст согласно шаблону
def modification_data(outlets):
    try:
        with open(INPUT_FILE, 'r') as data:
            search_string = 'APC-Outlets'
            text = data.read()
            matched_user = None
            modified_text = ''
            for line_number, line_data in enumerate(text.splitlines()):
                match = re.fullmatch(r'^([\w\d.]+)\s*$', line_data)
                if match:
                    matched_user = match.group(1)
                else:
                    match = re.fullmatch(r'^\s+' + search_string + r'.*\"\s*$', line_data)
                    if match and matched_user == USERNAME:
                        logging.debug('Строка для изменения значений на строке номер %s', line_number)
                        logging.debug('Старые данные %s', line_data)
                        line_data = "\t\t\tAPC-Outlets = \"1[" + outlets + "];\""
                        logging.debug('Новые данные %s', line_data)
                modified_text += line_data + '\n'
                with open(OUTPUT_FILE, "w") as mod_data:
                    mod_data.write(modified_text)
    except Exception as e:
        logging.warning(e)


def ready_to_go(outlets):
    try:
        s = ','
        if s not in outlets:
            logging.info('Розетка номер ' + outlets + ' готова к работе!')
            print(TextColor.Green + 'Розетка номер ' + outlets + ' готова к работе!' + TextColor.END)
        elif outlets:
            logging.info('Розетки номер ' + outlets + ' готовы к работе!')
            print(TextColor.Green + 'Розетки номер ' + outlets + ' готовы к работе!' + TextColor.END)
    except Exception as e:
        logging.warning(e)


def main():
    check_username()
    outlets = input_data()
    modification_data(outlets)
    ready_to_go(outlets)


if __name__ == '__main__':
    main()
