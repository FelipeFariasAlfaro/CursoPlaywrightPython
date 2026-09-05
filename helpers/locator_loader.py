import json
import os
import warnings

LOCATORS_DIR = os.path.join(os.path.dirname(__file__), '..', 'locators')


def _load_single(filename):
    """Carga un único archivo JSON de localizadores buscando en /locators/."""
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


def load_locators(*filenames):
    """
    Carga localizadores desde uno o varios archivos JSON, buscando
    recursivamente en todas las subcarpetas de /locators/.

    Acepta el nombre con o sin extensión .json.

    Uso con un solo archivo:
        locators = load_locators('tiendaqa')
        locators = load_locators('tiendaqa.json')

    Uso con varios archivos (se combinan en un solo diccionario):
        locators = load_locators('tiendaqa', 'formulario')
        locators = load_locators(['tiendaqa', 'formulario'])

    Luego:
        page.locator(locators['titulo']).click()

    Si dos archivos definen la misma clave, prevalece el último cargado
    y se emite una advertencia para evitar colisiones silenciosas.
    """
    # Permitir pasar una lista/tupla como único argumento:
    # load_locators(['tiendaqa', 'formulario'])
    if len(filenames) == 1 and isinstance(filenames[0], (list, tuple)):
        filenames = tuple(filenames[0])

    if not filenames:
        raise ValueError("Debes indicar al menos un archivo de localizadores.")

    combinado = {}
    for filename in filenames:
        locators = _load_single(filename)

        claves_repetidas = set(combinado) & set(locators)
        if claves_repetidas:
            warnings.warn(
                f"Claves de localizadores duplicadas al cargar '{filename}': "
                f"{sorted(claves_repetidas)}. Se usará el valor de '{filename}'.",
                stacklevel=2,
            )

        combinado.update(locators)

    return combinado
