from behave import given, when, then
from helpers.locator_loader import load_locators

selectores = load_locators('tiendaqa.json')

@given('ingreso a la página "{url}"')
def step_ingreso_a_pagina(context, url):
    context.page.goto(url)

@given(u'hago click en "{element}"') #primer_producto
def step_impl(context, element):
   elemento_web = context.page.locator(selectores[element])
   elemento_web.click()
   context.page.wait_for_timeout(5000)

@given(u'presiono el elemento "{elemento}" un numero de {cantidad:d} veces')
def step_impl(context, elemento, cantidad):
    elemento_web = context.page.locator(selectores[elemento])
    for _ in range(cantidad):
        elemento_web.click()

@given(u'ingreso el texto "{texto}" en el campo "{localizador}"')
def step_impl(context, texto, localizador):
    input_web = context.page.locator(selectores[localizador])      
    input_web.fill(texto)

@given(u'ingreso "{texto}" en el campo "{localizador}" con delay de {tiempo:d} ms')
def step_impl(context, texto, localizador, tiempo):
    input_web = context.page.locator(selectores[localizador])
    input_web.press_sequentially(texto, delay=tiempo)


@given(u'espero {segundos:d} segundos')
def step_espera(context, segundos):
    context.page.wait_for_timeout(segundos * 1000)