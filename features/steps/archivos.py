
import os
from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect

selectores = load_locators('archivos')

@step(u'cargo el archivo "{nombre_archivo}" en el campo de carga "{localizador}"')
def step_cargar_archivo(context, nombre_archivo, localizador):
    # Obtener el directorio desde el .env (por defecto 'uploads' si no está definido)
    carpeta_uploads = os.getenv('UPLOADS_DIR')

    # Calcular la ruta raíz del proyecto (subiendo desde features/steps/)
    ruta_proyecto = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Unir la ruta raíz con la carpeta configurada en el .env y el nombre del archivo
    ruta_archivo = os.path.join(ruta_proyecto, carpeta_uploads, nombre_archivo)

    # Cargar el archivo usando Playwright
    input_file = context.page.locator(selectores[localizador])
    input_file.set_input_files(ruta_archivo)
