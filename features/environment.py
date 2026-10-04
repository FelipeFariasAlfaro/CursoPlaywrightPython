import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from playwright.sync_api import sync_playwright
from helpers.report_generator import ReportCollector, REPORT_ENABLED
from helpers.trace_manager import iniciar_trace, guardar_trace

# Timeouts globales (en milisegundos)
DEFAULT_TIMEOUT = 10000        # Timeout para acciones (click, fill, etc.)
NAVIGATION_TIMEOUT = 30000     # Timeout para navegación (goto, reload, etc.)


def _asegurar_navegador(context):
    """Lanza el navegador solo la primera vez que se necesita (perezoso).

    Así, una ejecución 100% de API (@api) nunca abre navegador.
    """
    if getattr(context, 'browser', None) is not None:
        return

    headless = os.getenv('HEADLESS', 'false').lower() in ('true', '1', 'yes', 'si')
    context.browser = context.playwright.chromium.launch(
        headless=headless,
        args=["--start-maximized"]
    )


def before_all(context):
    """Inicia Playwright y el colector de reportes antes de todas las pruebas."""
    # El navegador NO se lanza aquí: se abre bajo demanda en el primer
    # escenario que lo necesite (ver _asegurar_navegador).
    context.playwright = sync_playwright().start()
    context.browser = None

    # Inicializar reporte
    context.report = ReportCollector()
    context.report.initialize()


def before_feature(context, feature):
    """Registra el inicio de una feature en el reporte."""
    context.report.start_feature(feature)


def before_scenario(context, scenario):
    """Crea una nueva página antes de cada escenario en pantalla completa."""

    # Tags del escenario + los heredados de la feature (Behave no los une solo).
    tags = set(scenario.tags) | set(scenario.feature.tags)

    # Escenarios de API no necesitan navegador: no lo abrimos.
    context.browser_context = None
    context.page = None
    if "api" in tags:
        context.report.start_scenario(scenario)
        return

    # Para el resto, aseguramos el navegador (se abre la primera vez).
    _asegurar_navegador(context)

    if "view_mobile" in tags:
        dispositivo = context.playwright.devices["iPhone 13"]
        context.browser_context = context.browser.new_context(**dispositivo)
        context.page = context.browser_context.new_page()

    else:     
        context.browser_context = context.browser.new_context(no_viewport=True, 
                                                              permissions=["geolocation"])
        context.page = context.browser_context.new_page()


    context.page.set_default_timeout(DEFAULT_TIMEOUT)
    context.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    iniciar_trace(context)

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
    context.report.end_scenario(scenario)

    # Escenarios de API no abrieron navegador: nada que cerrar ni traza.
    if getattr(context, 'browser_context', None) is None:
        return

    guardar_trace(context, scenario)   # antes de cerrar el contexto
    context.browser_context.close()


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
