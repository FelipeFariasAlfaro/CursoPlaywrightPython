
import os
from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect
from helpers.report_generator import PROJECT_ROOT

selectores = load_locators()

@step(u'cargo el archivo "{nombre_archivo}" en el campo de carga "{localizador}"')
def step_cargar_archivo(context, nombre_archivo, localizador):
    # Obtener el directorio desde el .env (por defecto 'uploads' si no está definido)
    carpeta_uploads = os.getenv('UPLOADS_DIR')

    # Raíz del proyecto confiable, calculada desde helpers/ (no depende
    # de la profundidad de este archivo dentro de features/steps/)
    ruta_archivo = os.path.join(str(PROJECT_ROOT), carpeta_uploads, nombre_archivo)

    input_file = context.page.locator(selectores[localizador])
    input_file.set_input_files(ruta_archivo)
