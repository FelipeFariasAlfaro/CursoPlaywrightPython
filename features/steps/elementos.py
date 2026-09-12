from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect

selectores = load_locators('elementos')

@step(u'hago scroll al fondo de la pagina')
def step_impl(context):
    #context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    context.page.keyboard.press("End")

@step(u'muevo el elemento de rango hasta el valor de {valor:d}')
def step_impl(context, valor):
    valor_pred = 50

    rango = context.page.locator(selectores['pe_rango'])
    rango.focus()

    diferencia = valor - valor_pred

    if diferencia > 0:
        for _ in range(diferencia):
            context.page.keyboard.press("ArrowRight")

    elif diferencia < 0:
        for _ in range(abs(diferencia)):
                    context.page.keyboard.press("ArrowLeft")
                    

@step(u'valido que el valor final es {valorFinal:d}')
def step_impl(context, valorFinal):

    valor_label = context.page.locator(selectores['valor_rango'])

    texto_valor = valor_label.inner_text().strip()

    valor_obtenido = int(texto_valor)

    assert valor_obtenido == valorFinal, f"Falló: Se esperaba {valorFinal} pero se obtiene {valor_obtenido}"





    

