"""
Steps genéricos para pruebas de API REST usando helpers/api_client.py.

Cubren: GET, POST, PUT, PATCH, DELETE, base URL, headers, y aserciones de
status, valores, estructura y tipos de datos.
"""

import json
from behave import given, when, then, step
from helpers.api_client import ApiClient


# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL CLIENTE
# ══════════════════════════════════════════════════════════════

@given('que uso la API base "{base_url}"')
def step_impl(context, base_url):
    # Crea el cliente con una base URL explícita (ignora la del .env).
    context.api = ApiClient(context, base_url=base_url)


@given('que uso la API configurada por defecto')
def step_impl(context):
    # Crea el cliente usando API_BASE_URL del .env.
    context.api = ApiClient(context)


@given('agrego el header "{clave}" con valor "{valor}"')
def step_impl(context, clave, valor):
    context.api.set_header(clave, valor)


# ══════════════════════════════════════════════════════════════
# MÉTODOS HTTP
# ══════════════════════════════════════════════════════════════

@when('hago una peticion GET a "{ruta}"')
def step_impl(context, ruta):
    context.respuesta = context.api.get(ruta)


@when('hago una peticion POST a "{ruta}" con el cuerpo')
def step_impl(context, ruta):
    # El cuerpo viene como bloque de texto JSON debajo del step (docstring).
    cuerpo = json.loads(context.text)
    context.respuesta = context.api.post(ruta, data=cuerpo)


@when('hago una peticion PUT a "{ruta}" con el cuerpo')
def step_impl(context, ruta):
    cuerpo = json.loads(context.text)
    context.respuesta = context.api.put(ruta, data=cuerpo)


@when('hago una peticion PATCH a "{ruta}" con el cuerpo')
def step_impl(context, ruta):
    cuerpo = json.loads(context.text)
    context.respuesta = context.api.patch(ruta, data=cuerpo)


@when('hago una peticion DELETE a "{ruta}"')
def step_impl(context, ruta):
    context.respuesta = context.api.delete(ruta)


# ══════════════════════════════════════════════════════════════
# ASERCIONES
# ══════════════════════════════════════════════════════════════

@then('el status de la respuesta es {codigo:d}')
def step_impl(context, codigo):
    context.respuesta.validar_status(codigo)


@then('el campo "{ruta}" vale "{esperado}"')
def step_impl(context, ruta, esperado):
    context.respuesta.validar_valor(ruta, esperado)


@then('el campo "{ruta}" vale el numero {esperado:d}')
def step_impl(context, ruta, esperado):
    context.respuesta.validar_valor(ruta, esperado)


@then('la respuesta tiene los campos')
def step_impl(context):
    # Lista de campos, uno por fila en una tabla con encabezado "campo".
    campos = [fila["campo"] for fila in context.table]
    context.respuesta.validar_estructura(campos)


@then('el campo "{ruta}" es de tipo "{tipo}"')
def step_impl(context, ruta, tipo):
    context.respuesta.validar_tipo(ruta, tipo)


@then('cierro la conexion de la API')
def step_impl(context):
    context.api.cerrar()
