"""
Trace Viewer de Playwright para Behave.

Graba la ejecución de cada escenario para poder depurarla luego con:
    playwright show-trace <archivo.zip>

Se configura por .env:
    TRACE_ENABLED=true            # activar/desactivar
    TRACE_ONLY_ON_FAILURE=true    # grabar solo escenarios que fallan
    TRACE_OUTPUT_DIR=reports/traces

Integración en environment.py (solo 2 líneas):
    from helpers.trace_manager import iniciar_trace, guardar_trace

    def before_scenario(context, scenario):
        iniciar_trace(context)

    def after_scenario(context, scenario):
        guardar_trace(context, scenario)   # antes de cerrar el contexto
"""

import os
from pathlib import Path


def _env_bool(clave, defecto=False):
    return os.getenv(clave, str(defecto)).lower() in ('true', '1', 'yes', 'si')


TRACE_ENABLED = _env_bool('TRACE_ENABLED', False)
TRACE_ONLY_ON_FAILURE = _env_bool('TRACE_ONLY_ON_FAILURE', True)
TRACE_OUTPUT_DIR = os.getenv('TRACE_OUTPUT_DIR', 'reports/traces')


def _nombre_seguro(texto):
    """Convierte el nombre de un escenario en un nombre de archivo válido."""
    return "".join(
        c if c.isalnum() or c in (' ', '-', '_') else '_' for c in texto
    )[:60].strip()


def iniciar_trace(context):
    """Inicia la grabación del trace en el contexto actual, si está activo."""
    if not TRACE_ENABLED:
        return
    context.browser_context.tracing.start(
        screenshots=True,   # imágenes en cada acción
        snapshots=True,     # DOM inspeccionable en cada paso
        sources=True,       # código fuente de los steps
    )


def guardar_trace(context, scenario):
    """
    Detiene la grabación y guarda el .zip si corresponde.
    Debe llamarse ANTES de cerrar el browser_context.
    """
    if not TRACE_ENABLED or not hasattr(context, 'browser_context'):
        return

    # Con TRACE_ONLY_ON_FAILURE, solo guardamos escenarios fallidos.
    guardar = (not TRACE_ONLY_ON_FAILURE) or (scenario.status == 'failed')

    if guardar:
        carpeta = Path(TRACE_OUTPUT_DIR)
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta / f"{_nombre_seguro(scenario.name)}.zip"
        context.browser_context.tracing.stop(path=str(ruta))
        print(f'[TRACE] Guardado: {ruta}  (ábrelo con: playwright show-trace "{ruta}")')
    else:
        # Escenario pasó y solo grabamos fallos: descartamos el trace.
        context.browser_context.tracing.stop()
