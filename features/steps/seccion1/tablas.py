
from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect


selectores = load_locators('tablas')

#@then(u'valido que los elementos de la columna "{header1}"con localizador "{xpath}" son correctos')
#def step_impl(context, header1, xpath):
    #guarda el contenido de la tabla en paises esperados
#    paises_esperados = [row[header1] for row in context.table]

    #extraemos los elementos de la tabla web
#    columna_paises = context.page.locator(selectores[xpath])

#    expect(columna_paises).to_have_text(paises_esperados)


@step(u'valido que los elementos de la columna "{header1}" con localizador "{xpath}" son correctos')
def step_impl(context, header1, xpath):
    valores_esperados = [row[header1].strip() for row in context.table]

    columna = context.page.locator(selectores[xpath])
    valores_en_tabla = [texto.strip() for texto in columna.all_inner_texts()]

    for i in range(len(valores_esperados)):
        esperado = valores_esperados[i]
        obtenido = valores_en_tabla[i]
        fila = i + 1  # +1 para que la primera fila sea 1 y no 0

        assert esperado == obtenido, (
            f"Falló en la fila {fila} de la columna '{header1}':\n"
            f"  Esperado : '{esperado}'\n"
            f"  Obtenido : '{obtenido}'"
        )       


