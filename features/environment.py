import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from playwright.sync_api import sync_playwright

# Timeouts globales (en milisegundos)
DEFAULT_TIMEOUT = 10000        # Timeout para acciones (click, fill, etc.)
NAVIGATION_TIMEOUT = 30000     # Timeout para navegación (goto, reload, etc.)


def before_all(context):
    """Inicia Playwright antes de todas las pruebas."""
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )


def before_scenario(context, scenario):
    """Crea una nueva página antes de cada escenario en pantalla completa."""
    context.page = context.browser.new_page(no_viewport=True)
    # Configurar timeouts globales para la página
    context.page.set_default_timeout(DEFAULT_TIMEOUT)
    context.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)


def after_scenario(context, scenario):
    """Cierra la página después de cada escenario."""
    if hasattr(context, 'page') and context.page:
        context.page.close()


def after_all(context):
    """Cierra el navegador y Playwright después de todas las pruebas."""
    if hasattr(context, 'browser') and context.browser:
        context.browser.close()
    if hasattr(context, 'playwright') and context.playwright:
        context.playwright.stop()
