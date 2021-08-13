from search_engine.transliterations import Transliterations
import json
import re

with open('search_engine/clients.json', 'r') as dict_with_clients:
    clients = json.loads(dict_with_clients.read())
    clients_names = clients.keys()

def transliteration(client):
    translations = [client]
    for dictionary in Transliterations.dictionaries:
        word = ''
        for letter in client:
            try:
                word += dictionary[letter]
            except KeyError:
                word += letter
        if word not in translations and word != client:
            translations.append(word)
    return translations

def search(client):
    search_names = transliteration(client)

    coincidence_names = []
    for client_name in clients_names:
        for search_name in search_names:
            pattern = f'{search_name}[  \-\'\w]*'

            if re.match(pattern, client_name):
                coincidence_names.append(client_name)

    if not coincidence_names:
        return False

    elif len(coincidence_names) == 1:
        #тут должно быть обращение к свичу
        return coincidence_names[0], clients[coincidence_names[0]]

    return coincidence_names