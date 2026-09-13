
Feature: Pruebas en elementos web variados

    @elemento_rango
    Scenario: Prueba en rango web
        Given ingreso a la página "https://centyc.cl/pruebas/elementos-web"
        And hago click en "pe_menu_elementos"
        And hago scroll al fondo de la pagina
        When muevo el elemento de rango hasta el valor de 10
        Then valido que el valor final es 10


    @elemento_tabs
    Scenario: Pruebas con tabs cerrando post uso
        Given ingreso a la página "https://centyc.cl/"   
        And abro una nueva pestaña con la URL "https://centyc.cl/pruebas/elementos-web"
        And hago click en "pe_menu_elementos"
        And hago scroll al fondo de la pagina
        When muevo el elemento de rango hasta el valor de 10
        And vuelvo a la pestaña original
        And hago scroll al fondo de la pagina
        And espero 5 segundos

    @elemento_tabs_2
    Scenario: Pruebas con tabs moviendome post uso sin cerrar
        Given ingreso a la página "https://centyc.cl/"   
        And abro una nueva pestaña con la URL "https://centyc.cl/pruebas/elementos-web"
        And hago click en "pe_menu_elementos"
        And hago scroll al fondo de la pagina
        When muevo el elemento de rango hasta el valor de 10
        And vuelvo a la pestaña original sin cerrar la nueva
        And hago scroll al fondo de la pagina
        And espero 5 segundos    





