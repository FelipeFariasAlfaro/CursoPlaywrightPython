
from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect
from time import sleep
import time

selectores = load_locators()

@step(u'dibujo un cuadrado en la pizarra "{localizador}" de lado {lado:d}')
def step_impl(context, localizador, lado):

    pizarra = context.page.locator(selectores[localizador])

    # 1. Obtenemos la posición y tamaño reales del canvas en pantalla.
    caja = pizarra.bounding_box()

    # 2. Definimos la esquina de inicio con un margen desde el borde
    #    del canvas, para que el cuadrado quede dentro del área visible.
    margen = 80
    x_inicio = caja["x"] + margen
    y_inicio = caja["y"] + margen

    # 3. Calculamos las 4 esquinas del cuadrado a partir del inicio y el lado.
    esquina_superior_izq = (x_inicio,        y_inicio)
    esquina_superior_der = (x_inicio + lado,  y_inicio)
    esquina_inferior_der = (x_inicio + lado,  y_inicio + lado)
    esquina_inferior_izq = (x_inicio,         y_inicio + lado)

    # 4. Dibujamos: bajamos el mouse en la esquina 1 y recorremos las demás
    #    con el botón presionado, cerrando en la esquina inicial.
    mouse = context.page.mouse

    mouse.move(esquina_superior_izq[0], esquina_superior_izq[1])
    mouse.down()
    mouse.move(esquina_superior_der[0], esquina_superior_der[1])
    sleep(1)
    mouse.move(esquina_inferior_der[0], esquina_inferior_der[1])
    sleep(1)
    mouse.move(esquina_inferior_izq[0], esquina_inferior_izq[1])
    sleep(1)
    mouse.move(esquina_superior_izq[0], esquina_superior_izq[1])
    sleep(1)
    mouse.up() #levantamos el click del mouse para dejar de dibujar


@step(u'muevo el elemento "{objeto}" una distancia de {dx:d} en x y {dy:d} en y')
def step_impl(context, objeto, dx, dy):
    elemento = context.page.locator(selectores[objeto])
    elemento.scroll_into_view_if_needed()

    caja = elemento.bounding_box()
    x = caja["x"] + caja["width"] / 2
    y = caja["y"] + caja["height"] / 2

    mouse = context.page.mouse
    mouse.move(x, y)
    mouse.down()

    # Pasos intermedios: Angular CDK necesita movimiento progresivo
    pasos = 10
    for i in range(1, pasos + 1):
        ix = x + dx * i / pasos
        iy = y + dy * i / pasos
        mouse.move(ix, iy)

    mouse.up()