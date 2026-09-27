Feature: Login de ingreso a centyc

    @login_test1
    Scenario: Verificar mensajes al no seleccionar el check de aceptacióno
        Given ingreso a la página "https://centyc.cl/pruebas/elementos-web"
        And hago click en "tab_formulario1"
        And ingreso el texto "felipe.farias@centyc.cl" en el campo "campo_usuario_login"
        And ingreso el texto "demo1234" en el campo "campo_pass_login"
        When hago click en "btn_send_login"
        Then verifico que aparece error solo en el mensaje del check
