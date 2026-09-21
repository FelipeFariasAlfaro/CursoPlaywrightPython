from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect

selectores = load_locators('formulario')

@step(u'selecciono en el elemento "{localizador}" la opción "{opcion}"')
def step_selecciono_opcion_formulario(context, localizador, opcion):

    context.page.locator(selectores[localizador]).select_option(opcion)

    """
        Opción viable según el sistema
    context.page.locator(selectores[localizador]).click()
    opcionSel = context.page.get_by_role("option", name=opcion)
    opcionSel.wait_for(state="visible")
    opcionSel.click()
    """

@step(u'hago click en el color "{color}"')
def step_seleccioanr_color(context, color):
    color = context.page.locator(color)
    color.click();
    