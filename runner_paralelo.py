import subprocess
import sys
import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from helpers.report_consolidator import consolidar_reportes
from helpers.report_generator import PROJECT_ROOT, CONSOLIDATED_DIR

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════

# Tag a ejecutar. Se buscarán todas las features que lo contengan y se
# repartirán entre los workers.
TAG = '@prueba_paralela'

# Cuántos procesos (workers) corren a la vez. Las features se reparten
# automáticamente entre ellos.
MAX_WORKERS = 2

# Carpeta donde viven los .feature.
FEATURES_DIR = PROJECT_ROOT / 'features' / 'pruebas'


# ══════════════════════════════════════════════════════════════
# DESCUBRIMIENTO DE FEATURES POR TAG
# ══════════════════════════════════════════════════════════════

def features_con_tag(tag):
    """
    Devuelve la lista de archivos .feature que contienen el tag indicado
    (ya sea a nivel de Feature o de algún Scenario dentro de ella).
    """
    tag_limpio = tag if tag.startswith('@') else f'@{tag}'
    encontradas = []

    for ruta in sorted(FEATURES_DIR.rglob('*.feature')):
        texto = ruta.read_text(encoding='utf-8')
        for linea in texto.splitlines():
            linea = linea.strip()
            # Las líneas de tags empiezan con @ y pueden tener varios tags.
            if linea.startswith('@') and tag_limpio in linea.split():
                encontradas.append(ruta)
                break

    return encontradas


# ══════════════════════════════════════════════════════════════
# EJECUCIÓN DE UNA FEATURE (un worker)
# ══════════════════════════════════════════════════════════════

def ejecutar_feature(ruta_feature):
    """Ejecuta UNA feature filtrando por el tag, en su propio proceso."""
    relativa = ruta_feature.relative_to(FEATURES_DIR)
    nombre = str(relativa.with_suffix('')).replace(os.sep, '_')

    entorno = os.environ.copy()
    # Modo consolidado: cada proceso guarda datos crudos, no genera HTML propio
    # y no limpia la carpeta compartida.
    entorno['REPORT_CONSOLIDATED'] = 'true'
    entorno['REPORT_CLEAN_BEFORE_RUN'] = 'false'
    entorno['SCREENSHOTS_DIR'] = f'reports/_consolidado_data/screenshots_{nombre}'

    # Ejecutamos SOLO esta feature y SOLO los escenarios con el tag.
    command = [
        sys.executable, '-m', 'behave',
        '--no-capture', '--no-skipped',
        '--tags', TAG,
        str(ruta_feature),
    ]

    print(f"[INICIO] {relativa}")
    resultado = subprocess.run(command, env=entorno).returncode
    print(f"[FIN] {relativa} (código {resultado})")
    return resultado


# ══════════════════════════════════════════════════════════════
# ORQUESTACIÓN
# ══════════════════════════════════════════════════════════════

def ejecutar_en_paralelo():
    features = features_con_tag(TAG)

    if not features:
        print(f"No se encontró ninguna feature con el tag {TAG}")
        return 1

    print(f"Tag {TAG}: {len(features)} feature(s) encontradas. "
          f"Repartiendo entre {MAX_WORKERS} worker(s).")
    for f in features:
        print(f"   - {f.relative_to(FEATURES_DIR)}")

    # Limpiamos la carpeta de datos crudos una sola vez antes de empezar.
    shutil.rmtree(PROJECT_ROOT / CONSOLIDATED_DIR, ignore_errors=True)

    # ThreadPoolExecutor.map reparte las features entre los workers:
    # cuando un worker termina su feature, toma la siguiente disponible.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        resultados = list(executor.map(ejecutar_feature, features))

    # Con todos los procesos terminados, generamos el reporte unificado.
    consolidar_reportes()

    return 0 if all(r == 0 for r in resultados) else 1


if __name__ == "__main__":
    sys.exit(ejecutar_en_paralelo())
