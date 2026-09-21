

from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect
from time import sleep
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


selectores = load_locators()

@then(u'la página "{url}" debe cargar en menos de {segundos:d} segundos')
def step_impl(context, url, segundos):
    #establecemos el inicio del contador de tiempo
    inicio = time.perf_counter()
    #vamos a la URL
    context.page.goto(url)

    transcurrido = time.perf_counter() - inicio 
    print(f"La página cargó en {transcurrido:.2f} segundos")

    assert transcurrido < segundos, (f"La página tardó {transcurrido:.2f}s, se esperaba menos de  {segundos} segundo(s)")


@then(u'al hacer click en "{elemento}" el servicio "{url_servicio}" debe responder en menos de {tiempo:d} ms')
def step_impl(context, elemento, url_servicio, tiempo):
    inicio = time.perf_counter()

    try:
        with context.page.expect_response(lambda r: url_servicio in r.url) as info_response:
            context.page.locator(selectores[elemento]).click()
    except PlaywrightTimeoutError:
            assert False, (
                 f"El servicio {url_servicio} no respondió en {tiempo} ms "
                 f"(o nunca fue llamado: revisa la URL, tal vez es incorrecta)"
            )

    respuesta = info_response.value
    trascurrido_ms = (time.perf_counter() - inicio) * 1000 

    assert respuesta.status == 200, f"El servicio respondio con el status {respuesta.status}"  
    assert trascurrido_ms < tiempo, (
        f"El servicio tardó {trascurrido_ms}:.0f ms, se esperaba menos de {tiempo} ms"
    )


## EXTRA EXTRA EXTRA ## 

"""
    Verifica un servicio al cargar una url
"""
@step(u'al cargar "{url}" el servicio "{url_servicio}" debe responder en menos de {ms:d} ms')
def step_impl(context, url, url_servicio, ms):
    inicio = time.perf_counter()

    # Empezamos a escuchar ANTES de navegar; el goto va dentro del bloque
    with context.page.expect_response(lambda r: url_servicio in r.url) as info:
        context.page.goto(url)

    respuesta = info.value
    transcurrido_ms = (time.perf_counter() - inicio) * 1000

    print(f"El servicio respondió en {transcurrido_ms:.0f} ms, status {respuesta.status}")

    assert respuesta.status == 200, f"El servicio respondió {respuesta.status}"
    assert transcurrido_ms < ms, f"Tardó {transcurrido_ms:.0f} ms, esperado < {ms} ms"   


"""
Step doble, primero comienza la captura
"""
step(u'empiezo a monitorear el servicio "{url_servicio}"')
def step_impl(context, url_servicio):
    context.tiempos_servicio = {}

    def capturar(response):
        if url_servicio in response.url:
            # request.timing tiene los tiempos reales de red del navegador
            timing = response.request.timing
            # responseEnd - startTime = duración total de la petición en ms
            duracion = timing["responseEnd"] - timing["startTime"]
            context.tiempos_servicio[response.url] = {
                "status": response.status,
                "duracion_ms": duracion,
            }

    context.page.on("response", capturar)     

"""
    Segundo Step complementa al anterior, este permite medir cuanto tardó la respuesta
    Ej de uso completo
    
    Scenario: El servicio de la home responde rápido al cargar
        Given empiezo a monitorear el servicio "/api/productos"
        And ingreso a la página "https://centyc.cl/tiendaqa"
        Then el servicio "/api/productos" respondió en menos de 800 ms
"""
@step(u'el servicio "{url_servicio}" respondió en menos de {ms:d} ms')
def step_impl(context, url_servicio, ms):
    # Buscar la respuesta capturada que coincida
    encontrado = None
    for url, datos in context.tiempos_servicio.items():
        if url_servicio in url:
            encontrado = datos
            break

    assert encontrado is not None, f"No se capturó ninguna llamada a '{url_servicio}'"
    print(f"El servicio respondió en {encontrado['duracion_ms']:.0f} ms")

    assert encontrado["status"] == 200
    assert encontrado["duracion_ms"] < ms, (
        f"Tardó {encontrado['duracion_ms']:.0f} ms, esperado < {ms} ms"
    )