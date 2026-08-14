import subprocess
import sys

def ejecutar_tests(tags='@centyc-e2e'):

    command = [sys.executable, '-m', 'behave', '--no-capture', '--no-skipped']
    command.extend(['--tags', tags])
    
    try:
        return subprocess.run(command).returncode
    except Exception as e:
        print(f"[ERROR] Hay un problema con la ejecución: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(ejecutar_tests())    