"""
Consolidador de Reportes HTML.

Une los datos crudos (JSON) que dejan las ejecuciones paralelas en la carpeta
compartida y genera UN SOLO reporte HTML, reutilizando toda la lógica de
presentación de ReportCollector.

Uso:
    from helpers.report_consolidator import consolidar_reportes
    consolidar_reportes()

Normalmente lo llama runner_paralelo.py al terminar todos los procesos.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

from helpers.report_generator import (
    ReportCollector,
    PROJECT_ROOT,
    CONSOLIDATED_DIR,
    REPORT_OUTPUT_DIR,
    REPORT_FILENAME,
)


def _parse_fecha(valor):
    """Convierte texto ISO de vuelta a datetime (o None si no hay valor)."""
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor)
    except (ValueError, TypeError):
        return None


def consolidar_reportes(salida=None, limpiar_datos=True):
    """
    Lee todos los JSON de datos de la carpeta compartida y genera un HTML único.

    Args:
        salida: ruta del HTML consolidado. Por defecto reports/<REPORT_FILENAME>.
        limpiar_datos: si True, borra la carpeta de datos crudos tras consolidar.

    Returns:
        La ruta del reporte generado, o None si no había datos.
    """
    carpeta_datos = PROJECT_ROOT / CONSOLIDATED_DIR

    if not carpeta_datos.exists():
        print("[CONSOLIDADO] No hay carpeta de datos; nada que consolidar.")
        return None

    archivos = sorted(carpeta_datos.glob("datos_*.json"))
    if not archivos:
        print("[CONSOLIDADO] No se encontraron datos de ejecuciones.")
        return None

    # Unir features de todos los procesos y calcular el rango de tiempo global.
    todas_features = []
    inicios = []
    finales = []

    for archivo in archivos:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        todas_features.extend(datos.get("features", []))

        inicio = _parse_fecha(datos.get("start_time"))
        fin = _parse_fecha(datos.get("end_time"))
        if inicio:
            inicios.append(inicio)
        if fin:
            finales.append(fin)

    # El inicio global es el más temprano y el fin el más tardío.
    start_time = min(inicios) if inicios else datetime.now()
    end_time = max(finales) if finales else datetime.now()

    # Reutilizamos ReportCollector para armar el HTML con la misma apariencia.
    collector = ReportCollector()
    collector.cargar_desde_datos(todas_features, start_time, end_time)

    # Ruta de salida del reporte consolidado.
    if salida is None:
        salida = PROJECT_ROOT / REPORT_OUTPUT_DIR / REPORT_FILENAME
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)

    collector.generar_html_en(salida)
    print(f"[CONSOLIDADO] Reporte único generado en: {salida}")

    # Limpiar los datos crudos para no acumular basura entre corridas.
    if limpiar_datos:
        shutil.rmtree(carpeta_datos, ignore_errors=True)

    return salida


if __name__ == "__main__":
    consolidar_reportes()
