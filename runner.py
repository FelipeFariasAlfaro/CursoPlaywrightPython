import subprocess
import sys
import os

# Tag por defecto para ejecución LOCAL (si no se indica otro).
TAG_POR_DEFECTO = '@regresion'


def obtener_tags():
    """
    Determina qué tag ejecutar, con esta prioridad:
      1. Argumento de línea de comandos:  python runner.py @smoke
      2. Variable de entorno BEHAVE_TAGS (la usa GitHub Actions)
      3. TAG_POR_DEFECTO (uso local)
    """
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.getenv('BEHAVE_TAGS', TAG_POR_DEFECTO)


def ejecutar_tests(tags=None):
    if tags is None:
        tags = obtener_tags()

    print(f"[RUNNER] Ejecutando pruebas con el tag: {tags}")

    command = [sys.executable, '-m', 'behave', '--no-capture', '--no-skipped']
    command.extend(['--tags', tags])

    try:
        return subprocess.run(command).returncode
    except Exception as e:
        print(f"[ERROR] Hay un problema con la ejecución: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(ejecutar_tests())
