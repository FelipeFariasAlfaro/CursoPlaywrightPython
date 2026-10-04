
from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect

selectores = load_locators()


@step(u'ingreso al iframe "{localizador}"')
def step_impl(context, localizador):
    context.frame_actual =  context.page.frame_locator(selectores[localizador])
    


@step(u'escribo "{mensaje}" en el campo "{localizador}" del iframe')
def step_impl(context, mensaje, localizador):
    context.frame_actual.locator(selectores[localizador]).fill(mensaje)
