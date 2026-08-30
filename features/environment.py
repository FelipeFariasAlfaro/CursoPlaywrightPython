import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from playwright.sync_api import sync_playwright
from helpers.report_generator import ReportCollector, REPORT_ENABLED

# Timeouts globales (en milisegundos)
DEFAULT_TIMEOUT = 10000        # Timeout para acciones (click, fill, etc.)
NAVIGATION_TIMEOUT = 30000     # Timeout para navegación (goto, reload, etc.)


def before_all(context):
    """Inicia Playwright y el colector de reportes antes de todas las pruebas."""
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )

    # Inicializar reporte
    context.report = ReportCollector()
    context.report.initialize()


def before_feature(context, feature):
    """Registra el inicio de una feature en el reporte."""
    context.report.start_feature(feature)


def before_scenario(context, scenario):
    """Crea una nueva página antes de cada escenario en pantalla completa."""
    context.page = context.browser.new_page(no_viewport=True)
    context.page.set_default_timeout(DEFAULT_TIMEOUT)
    context.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    # Registrar inicio de escenario
    context.report.start_scenario(scenario)


def after_step(context, step):
    """Captura screenshot y registra resultado de cada step."""
    if not REPORT_ENABLED:
        return

    screenshot_path = None
    if hasattr(context, 'page') and context.page:
        screenshot_path = context.report.capture_screenshot(
            context.page, step, context.scenario
        )

    context.report.record_step(step, screenshot_path)


def after_scenario(context, scenario):
    """Cierra la página y registra fin del escenario."""
    # Registrar fin de escenario
    context.report.end_scenario(scenario)

    if hasattr(context, 'page') and context.page:
        context.page.close()


def after_feature(context, feature):
    """Registra el fin de una feature en el reporte."""
    context.report.end_feature(feature)


def after_all(context):
    """Cierra el navegador, Playwright y genera el reporte final."""
    # Generar reporte HTML
    context.report.finalize()

    if hasattr(context, 'browser') and context.browser:
        context.browser.close()
    if hasattr(context, 'playwright') and context.playwright:
        context.playwright.stop()
