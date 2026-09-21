Feature: Dibujos arrastrando el mouse

    @dibujo_cuadrado
    Scenario: Dibujar un cuadrado en la pizarra
        Given ingreso a la página "https://centyc.cl/pruebas/elementos-web"
        And hago click en "menu_pizarra"
        When dibujo un cuadrado en la pizarra "elemento_pizarra" de lado 150
        And espero 5 segundos

    @DragAndDrop1
    Scenario: dragAndDrop_version1
        Given ingreso a la página "https://hakatools.hakalab.com/hakatools/interactions"
        And hago click en "menu_arrastrar_y_soltar"
        When muevo el elemento "seccion_arrastrable" una distancia de -200 en x y -400 en y
        And espero 5 segundos

