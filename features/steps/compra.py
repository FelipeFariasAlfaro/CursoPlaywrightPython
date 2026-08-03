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



