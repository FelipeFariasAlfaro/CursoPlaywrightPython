from behave import given, when, then
from helpers.locator_loader import load_locators

#locators = load_locators('tiendaqa')

@given('ingreso a la página "{url}"')
def step_ingreso_a_pagina(context, url):
    context.page.goto(url)

