import os
from pathlib import Path
from helpers.locator_loader import load_locators

AUTH_DIR = Path("auth_sessions")
selectores = load_locators()

class AuthManager:
    """Gestiona login con reutilización de sesión (storage_state)."""

    def __init__(self, context):
        self.context = context

    def ingresar(self, email, password):
        """Reutiliza la sesión si existe y sigue válida; si no, loguea."""
        ruta = self._ruta_estado(email)

        if ruta.exists():
            self._cargar_estado(ruta)
            if self._sesion_valida():
                print(f"[AUTH] Sesión reutilizada: {email}")
                return
            print(f"[AUTH] Sesión expirada, re-logueando: {email}")

        self._login(email, password)
        self._guardar_estado(ruta)
        print(f"[AUTH] Login realizado y guardado: {email}")

    # ─── privados ───

    def _ruta_estado(self, email):
        nombre = email.replace("@", "_").replace(".", "_")
        return AUTH_DIR / f"auth_{nombre}.json"

    def _cargar_estado(self, ruta):
        """Recrea el contexto cargando la sesión guardada."""
        self.context.browser_context.close()
        self.context.browser_context = self.context.browser.new_context(
            no_viewport=True,
            storage_state=str(ruta),
        )
        self.context.page = self.context.browser_context.new_page()

    def _sesion_valida(self):
        """Entra a una página protegida y verifica si seguimos logueados."""
        self.context.page.goto("https://centyc.cl/tiendaqa")
        return self.context.page.locator(selectores["validador_logeado"]).is_visible()

    def _login(self, email, password):
        page = self.context.page
        page.goto("https://centyc.cl/tiendaqa")
        page.locator(selectores["btn_iniciar_sesion"]).click()
        page.locator(selectores["input_user"]).fill(email)
        page.locator(selectores["input_pass"]).fill(password)
        self.context.page.wait_for_timeout(3 * 1000)
        page.locator(selectores["btn_login"]).click()
        

    def _guardar_estado(self, ruta):
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        self.context.browser_context.storage_state(path=str(ruta))
