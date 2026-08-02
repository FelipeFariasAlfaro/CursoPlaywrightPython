import json
import os

LOCATORS_DIR = os.path.join(os.path.dirname(__file__), '..', 'locators')


def load_locators(page_name):
    """
    Carga los localizadores desde un archivo JSON.

    Uso:
        locators = load_locators('practica')
        page.locator(locators['titulo']).click()
    """
    file_path = os.path.join(LOCATORS_DIR, f'{page_name}.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
