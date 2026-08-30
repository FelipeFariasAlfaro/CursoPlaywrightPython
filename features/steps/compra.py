from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect

selectores = load_locators('tiendaqa.json')

@step('ingreso a la página "{url}"')
def step_ingreso_a_pagina(context, url):
    context.page.goto(url)

@step(u'hago click en "{element}"') #primer_producto
def step_impl(context, element):
   elemento_web = context.page.locator(selectores[element])
   elemento_web.click()
   context.page.wait_for_timeout(5000)

@step(u'presiono el elemento "{elemento}" un numero de {cantidad:d} veces')
def step_impl(context, elemento, cantidad):
    elemento_web = context.page.locator(selectores[elemento])
    for _ in range(cantidad):
        elemento_web.click()

@step(u'ingreso el texto "{texto}" en el campo "{localizador}"')
def step_impl(context, texto, localizador):
    input_web = context.page.locator(selectores[localizador])      
    input_web.fill(texto)

@step(u'ingreso "{texto}" en el campo "{localizador}" con delay de {tiempo:d} ms')
def step_impl(context, texto, localizador, tiempo):
    input_web = context.page.locator(selectores[localizador])
    input_web.press_sequentially(texto, delay=tiempo)


@step(u'espero {segundos:d} segundos')
def step_espera(context, segundos):
    context.page.wait_for_timeout(segundos * 1000)


@step(u'el texto "{texto}" debe estar visible en pantalla')
def valida_texto(context, texto):
    expect(context.page.get_by_text(texto),
           f"[Error] Se esperaba ver el texto {texto} en pantalla.").to_be_visible()


@step(u'el elemento "{localizador}" debe contener el texto "{texto}"')
def validar_text_elemento(context, localizador, texto):
    expect(context.page.locator(selectores[localizador]),
           f"[ERROR] El elemento '{localizador}' no contiene el texto esperado.").to_have_text(texto)

@step(u'el elemento "{localizador}" debe ser visible en la pagina')
def validar_elemento_pantalla(context, localizador):
    expect( context.page.locator(selectores[localizador]),
           f"[ERROR] El elemento web con localizador '{localizador}' NO está visible en pantalla").to_be_visible()