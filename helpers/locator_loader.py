import json
import os

LOCATORS_DIR = os.path.join(os.path.dirname(__file__), '..', 'locators')


def load_locators(filename):
    """
    Carga los localizadores desde un archivo JSON, buscando recursivamente
    en todas las subcarpetas de /locators/.

    Acepta el nombre con o sin extensión .json:
        locators = load_locators('tiendaqa.json')
        locators = load_locators('tiendaqa')

    Uso:
        locators = load_locators('tiendaqa')
        page.locator(locators['titulo']).click()
    """
    if not filename.endswith('.json'):
        filename = f'{filename}.json'

    for root, _dirs, files in os.walk(LOCATORS_DIR):
        if filename in files:
            file_path = os.path.join(root, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

    raise FileNotFoundError(
        f"No se encontró '{filename}' en ninguna subcarpeta de {LOCATORS_DIR}"
    )
