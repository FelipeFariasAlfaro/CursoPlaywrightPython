@pruebas_logins @regresion
Feature: Pruebas con logins


    @login1
    Scenario: prueba login1
        Given ingreso sesión con "felipe.farias@centyc.cl" o utilizo la existente
        And espero 3 segundos
        Then el elemento "btn_cerrar_sesion" debe ser visible en la pagina

    @login2
    Scenario: prueba login2
        Given ingreso sesión con "felipe.farias@centyc.cl" o utilizo la existente
        And espero 3 segundos
        Then el elemento "btn_cerrar_sesion" debe ser visible en la pagina    