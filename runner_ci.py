"""
Runner para CI con sharding.

Dado UN tag, descubre las features que lo contienen y las REPARTE entre
varias máquinas (shards) de GitHub Actions. Cada máquina ejecuta solo la
porción de features que le corresponde.

Configuración por variables de entorno (las define el workflow):
    BEHAVE_TAGS   -> el tag a ejecutar (ej. @todas_las_apis)
    SHARD_INDEX   -> número de esta máquina (1, 2, 3, ...)
    SHARD_TOTAL   -> cuántas máquinas hay en total

Ejemplo: con 3 features [A, B, C] y SHARD_TOTAL=2:
    - máquina 1 (SHARD_INDEX=1) ejecuta A y C
    - máquina 2 (SHARD_INDEX=2) ejecuta B
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FEATURES_DIR = PROJECT_ROOT / 'features' / 'pruebas'

TAG = os.getenv('BEHAVE_TAGS', '@regresion')
SHARD_INDEX = int(os.getenv('SHARD_INDEX', '1'))
SHARD_TOTAL = int(os.getenv('SHARD_TOTAL', '1'))


def features_con_tag(tag):
    """Devuelve las features (.feature) que contienen el tag indicado."""
    tag_limpio = tag if tag.startswith('@') else f'@{tag}'
    encontradas = []
    for ruta in sorted(FEATURES_DIR.rglob('*.feature')):
        texto = ruta.read_text(encoding='utf-8')
        for linea in texto.splitlines():
            linea = linea.strip()
            if linea.startswith('@') and tag_limpio in linea.split():
                encontradas.append(ruta)
                break
    return encontradas


def features_de_este_shard(todas):
    """
    Reparte las features entre shards de forma determinista (round-robin).
    La máquina 'SHARD_INDEX' se queda con las posiciones index-1, +TOTAL, +2*TOTAL...
    """
    return [f for i, f in enumerate(todas) if i % SHARD_TOTAL == (SHARD_INDEX - 1)]


def ejecutar():
    todas = features_con_tag(TAG)
    if not todas:
        print(f"No se encontró ninguna feature con el tag {TAG}")
        return 1

    mias = features_de_este_shard(todas)

    print(f"Tag {TAG}: {len(todas)} feature(s) en total.")
    print(f"Shard {SHARD_INDEX}/{SHARD_TOTAL} ejecutará {len(mias)} feature(s):")
    for f in mias:
        print(f"   - {f.relative_to(FEATURES_DIR)}")

    if not mias:
        print("Este shard no tiene features asignadas. Nada que ejecutar.")
        return 0

    # Modo consolidado: cada shard guarda sus datos crudos (no genera HTML propio).
    # El reporte único lo arma el job final del workflow con el consolidador.
    entorno = os.environ.copy()
    entorno['REPORT_CONSOLIDATED'] = 'true'
    entorno['REPORT_CLEAN_BEFORE_RUN'] = 'false'

    # Ejecutamos todas las features de este shard en una sola corrida de Behave,
    # filtrando por el tag y pasando las rutas de las features asignadas.
    command = [sys.executable, '-m', 'behave', '--no-capture', '--no-skipped',
               '--tags', TAG]
    command.extend(str(f) for f in mias)

    return subprocess.run(command, env=entorno).returncode


if __name__ == "__main__":
    sys.exit(ejecutar())
