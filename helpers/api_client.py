"""
Cliente de API REST para pruebas, basado en la API request nativa de Playwright.

Ventajas:
- NO abre navegador (usa playwright.request, peticiones HTTP puras).
- Métodos GET, POST, PUT, DELETE, PATCH.
- Aserciones de status, valores, estructura y tipos de datos.
- Headers personalizados y base URL (desde .env con API_BASE_URL).
- Registra automáticamente request/response en el reporte HTML.

Uso típico en un step:
    from helpers.api_client import ApiClient

    @when('consulto el servicio GET "/todos/1"')
    def step_impl(context):
        context.api = ApiClient(context)        # context opcional (para el reporte)
        context.respuesta = context.api.get("/todos/1")

    @then('el status de la respuesta es {codigo:d}')
    def step_impl(context, codigo):
        context.respuesta.validar_status(codigo)
"""

import os
import json
from playwright.sync_api import sync_playwright

# Base URL para las llamadas (se puede sobreescribir al crear el cliente).
API_BASE_URL = os.getenv('API_BASE_URL', '')


# ══════════════════════════════════════════════════════════════
# RESPUESTA + ASERCIONES
# ══════════════════════════════════════════════════════════════

class ApiResponse:
    """Envuelve una respuesta HTTP y ofrece aserciones encadenables."""

    def __init__(self, status, body, headers):
        self.status = status
        self.body = body          # dict/list si era JSON, o texto si no
        self.headers = headers

    # ─── status ───

    def validar_status(self, esperado):
        """Verifica que el código de respuesta sea el esperado."""
        assert self.status == esperado, (
            f"Se esperaba status {esperado}, se obtuvo {self.status}. "
            f"Cuerpo: {self.body}"
        )
        return self

    # ─── valores ───

    def validar_valor(self, ruta, esperado):
        """
        Verifica que un campo tenga un valor exacto.
        'ruta' admite notación con puntos e índices: "usuario.nombre", "items.0.id".
        """
        obtenido = self._obtener(ruta)
        assert obtenido == esperado, (
            f"En '{ruta}' se esperaba {esperado!r}, se obtuvo {obtenido!r}"
        )
        return self

    # ─── estructura ───

    def validar_estructura(self, campos):
        """
        Verifica que existan las claves indicadas (lista de rutas).
        Ej: validar_estructura(["id", "usuario.nombre", "items.0.precio"])
        """
        faltantes = []
        for ruta in campos:
            if not self._existe(ruta):
                faltantes.append(ruta)
        assert not faltantes, f"Faltan campos en la respuesta: {faltantes}"
        return self

    # ─── tipos ───

    def validar_tipo(self, ruta, tipo_esperado):
        """
        Verifica el tipo de dato de un campo.
        'tipo_esperado' puede ser: "str", "int", "float", "bool", "list", "dict", "number".
        """
        valor = self._obtener(ruta)
        tipos = {
            'str': str, 'int': int, 'float': float, 'bool': bool,
            'list': list, 'dict': dict,
        }

        if tipo_esperado == 'number':
            ok = isinstance(valor, (int, float)) and not isinstance(valor, bool)
        elif tipo_esperado in tipos:
            esperado = tipos[tipo_esperado]
            # bool es subclase de int en Python: lo tratamos aparte
            if tipo_esperado == 'int':
                ok = isinstance(valor, int) and not isinstance(valor, bool)
            else:
                ok = isinstance(valor, esperado)
        else:
            raise ValueError(f"Tipo no soportado: {tipo_esperado}")

        assert ok, (
            f"En '{ruta}' se esperaba tipo '{tipo_esperado}', "
            f"se obtuvo {type(valor).__name__} (valor: {valor!r})"
        )
        return self

    # ─── acceso al cuerpo ───

    def valor(self, ruta):
        """Devuelve el valor de un campo por su ruta (para usar en el step)."""
        return self._obtener(ruta)

    def _obtener(self, ruta):
        """Navega el cuerpo con una ruta tipo 'a.b.0.c'."""
        actual = self.body
        for parte in str(ruta).split('.'):
            if isinstance(actual, list):
                actual = actual[int(parte)]
            elif isinstance(actual, dict):
                actual = actual[parte]
            else:
                raise AssertionError(f"No se puede acceder a '{parte}' en la ruta '{ruta}'")
        return actual

    def _existe(self, ruta):
        """Como _obtener, pero devuelve True/False en vez de lanzar error."""
        try:
            self._obtener(ruta)
            return True
        except (KeyError, IndexError, ValueError, AssertionError):
            return False


# ══════════════════════════════════════════════════════════════
# CLIENTE
# ══════════════════════════════════════════════════════════════

class ApiClient:
    """Cliente REST sobre la API request nativa de Playwright (sin navegador)."""

    def __init__(self, context=None, base_url=None, headers=None):
        """
        context: el context de Behave (opcional). Si se pasa:
                 - reutiliza su instancia de Playwright (context.playwright)
                 - registra las llamadas en el reporte HTML (context.report)
        base_url: URL base; si no se indica, usa API_BASE_URL del .env.
        headers:  headers por defecto para todas las llamadas de este cliente.
        """
        self._context = context
        self._base_url = base_url if base_url is not None else API_BASE_URL
        self._headers = dict(headers or {})

        # Reutilizamos el Playwright del context si existe (dentro de Behave);
        # si no (uso standalone), levantamos uno propio.
        pw_existente = getattr(context, 'playwright', None) if context else None
        if pw_existente is not None:
            self._pw = pw_existente
            self._pw_propio = False
        else:
            self._pw = sync_playwright().start()
            self._pw_propio = True

        self._request = self._pw.request.new_context(
            base_url=self._base_url or None,
            extra_http_headers=self._headers or None,
        )

    # ─── configuración ───

    def set_header(self, clave, valor):
        """Agrega o actualiza un header para las siguientes llamadas."""
        self._headers[clave] = valor
        # Recreamos el contexto request con los headers actualizados.
        self._request.dispose()
        self._request = self._pw.request.new_context(
            base_url=self._base_url or None,
            extra_http_headers=self._headers or None,
        )
        return self

    # ─── métodos HTTP ───

    def get(self, url, params=None):
        return self._enviar('GET', url, params=params)

    def post(self, url, data=None):
        return self._enviar('POST', url, data=data)

    def put(self, url, data=None):
        return self._enviar('PUT', url, data=data)

    def patch(self, url, data=None):
        return self._enviar('PATCH', url, data=data)

    def delete(self, url):
        return self._enviar('DELETE', url)

    # ─── núcleo ───

    def _enviar(self, metodo, url, data=None, params=None):
        kwargs = {}
        if data is not None:
            kwargs['data'] = data            # Playwright serializa dict/list a JSON
        if params is not None:
            kwargs['params'] = params

        respuesta_raw = self._request.fetch(url, method=metodo, **kwargs)

        # Intentamos parsear el cuerpo como JSON; si no, lo dejamos como texto.
        try:
            body = respuesta_raw.json()
        except Exception:
            body = respuesta_raw.text()

        status = respuesta_raw.status
        headers = respuesta_raw.headers

        # Registrar en el reporte si hay context con report disponible.
        self._registrar_en_reporte(metodo, url, status, data, body)

        return ApiResponse(status, body, headers)

    def _registrar_en_reporte(self, metodo, url, status, request_body, response_body):
        if self._context is None:
            return
        report = getattr(self._context, 'report', None)
        if report is None:
            return
        url_completa = f"{self._base_url}{url}" if self._base_url else url
        report.registrar_api(
            metodo=metodo,
            url=url_completa,
            status=status,
            request_body=request_body,
            response_body=response_body,
            request_headers=self._headers,
            ok=(200 <= status < 400),
        )

    def cerrar(self):
        """Libera los recursos del cliente. Llamar al terminar (ej. en after_scenario)."""
        self._request.dispose()
        # Solo detenemos Playwright si lo creamos nosotros (uso standalone).
        if self._pw_propio:
            self._pw.stop()
