from parsers import update_clients_database
from search_engine import search_engine
from console_output import print_nbi_header, console_output
import logging
import time

logging.basicConfig(filename="logs.txt", level=logging.INFO)


def update_db():
    print('Обновление базы данных, это может занять около 4-х минут...')
    start = time.time()
    logging.info("Вызов ф-ции update_db")
    update_clients_database.update_clients_data()
    print(f'-=База данных обновлена=-\nВремя обновления: {time.time() - start} сек.')


def main():
    while True:
        print_nbi_header()
        client = input('Введите имя клиента:').lower()

        if client == '--update':
            update_db()
            continue

        logging.info(f"Выполнить поиск клиента {client}")
        search_result = search_engine.search(client)

        if search_result == False:
            print('КЛИЕНТ НЕ НАЙДЕН')

        elif str(search_result.__class__) == "<class 'tuple'>":
            client_name = search_result[0]
            client_data = search_result[1]
            console_output(client_name, client_data)

        else:
            print('Выберите клиента:')
            print('-' * 100)
            for client_name in search_result:
                print(client_name)


if '__name__' == '__main__':
    pass
main()
