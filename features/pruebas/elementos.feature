
Feature: Pruebas en elementos web variados

    @elemento_rango
    Scenario: Prueba en rango web
        Given ingreso a la página "https://centyc.cl/pruebas/elementos-web"
        And hago click en "pe_menu_elementos"
        And hago scroll al fondo de la pagina
        When muevo el elemento de rango hasta el valor de 10
        Then valido que el valor final es 10