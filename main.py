from parsers import update_clients_database
from search_engine import search_engine
from console_output import print_nbi_header, console_output
from debugers import check_if_switch_in_client_notes
import logging
import time

logging.basicConfig(filename="logs.txt", level=logging.INFO)


def update_main_db():
    print('Обновление базы данных, это может занять около 4-х минут...')
    start = time.time()
    logging.info("Вызов ф-ции update_db")
    update_clients_database.update_clients_data('total')
    print(f'-=База данных обновлена=-\nВремя обновления: {time.time() - start} сек.')


def main():
    while True:
        print_nbi_header()
        client = input('Введите имя клиента:').lower()

        if client == '--update':
            update_main_db()
            continue

        if client == '--check':
            check_if_switch_in_client_notes.check()
            continue

        logging.info(f"***************************-={time.asctime(time.localtime())}=-***************************")
        logging.info(f"Выполнить поиск клиента {client}")
        search_result = search_engine.search(client)

        if search_result == False:
            print('КЛИЕНТ НЕ НАЙДЕН')

        elif str(search_result.__class__) == "<class 'tuple'>":
            client_name = search_result[0]
            client_data = search_result[1]
            logging.info(f"Данные о клиенте {client_name} переданы на вывод в консоль")
            console_output(client_name, client_data)

        else:
            print('Выберите клиента:')
            print('-' * 100)
            logging.info(f"По запросу найдены клиенты: {search_result}")
            for client_name in search_result:
                print(client_name)

        del search_result

if __name__ == '__main__':
    main()
