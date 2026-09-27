
from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from helpers.soft_assert import SoftAssert

selectores = load_locators()

@then(u'verifico que aparece error solo en el mensaje del check')
def step_impl(context):

    soft = SoftAssert()

    msg_usuario = context.page.locator(selectores['mensaje_usuario'])
    msg_password = context.page.locator(selectores['mensaje_password'])
    msg_check = context.page.locator(selectores['mensaje_sin_check'])

    soft.check(msg_usuario.is_visible(), "El mensaje válido para el nombre no aparece")
    soft.check(msg_password.is_visible(), "El mensaje válido para el password no aparece")
    soft.check(msg_check.is_visible(), "el mensaje de error por check no marcado no aparece")

    soft.assert_all()

    

