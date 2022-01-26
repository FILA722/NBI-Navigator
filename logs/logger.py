from datetime import datetime
from parsers.pathes import Pathes


def write_log(text: str):
    with open(Pathes.logs_client_migrations, 'a') as log_data:
        log_data.write(f'{datetime.now()} --> {text}\n')
