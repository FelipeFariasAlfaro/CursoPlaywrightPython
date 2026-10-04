Feature: Trabajo con iframes

    @iframe1
    Scenario: interacción con inputs de un iframes
        Given ingreso a la página "https://centyc.cl/pruebas/elementos-web"
        And hago click en "tab_iframe"
        When ingreso al iframe "iframe_simple"
        And escribo "Hola soy una prueba" en el campo "input_iframe" del iframe
        And espero 4 segundos
        And hago click en "tab_formulario1"