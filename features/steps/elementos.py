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


@step(u'abro una nueva pestaña con la URL "{url}"')
def step_impl(context, url):
    #asignamos la tab a un objeto temporal
    context.tab_original = context.page

    nueva_tab = context.page.context.new_page()
    nueva_tab.goto(url)

    context.page = nueva_tab



@step(u'vuelvo a la pestaña original')
def step_impl(context):
    context.page.close()
    context.page = context.tab_original

@step(u'vuelvo a la pestaña original sin cerrar la nueva')
def step_impl(context):
    context.tab_original.bring_to_front()
    context.page = context.tab_original






@step(u'marco el checkbox "{opcion_check}"')
def step_impl(context, opcion_check):
    context.page.locator(selectores[opcion_check]).check()
     

@step(u'el checkbox "{opcion_check}" debe estar marcado')
def step_impl(context, opcion_check):
    checkbox = context.page.locator(selectores[opcion_check])
    expect(checkbox).to_be_checked()
    

@step(u'desmarco el checkbox "{opcion_check}"')
def step_impl(context, opcion_check):
    checkbox = context.page.locator(selectores[opcion_check])
    checkbox.uncheck()
    

@step(u'el checkbox "{opcion_check}" no debe estar marcado')
def step_impl(context, opcion_check):
    checkbox = context.page.locator(selectores[opcion_check])
    expect(checkbox).not_to_be_checked()
     

 

    

