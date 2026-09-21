Feature: Pruebas de medición de tiempos de respuesta

    @prueba_tiempo1
    Scenario: Verificar tiempo de carga de una página
        Then la página "https://www.youtube.com/@CentycCl" debe cargar en menos de 5 segundos


    @prueba_tiempo2
    Scenario: medir tiempo de un servicio desde el frontend
        Given ingreso a la página "https://www.youtube.com/@CentycCl"
        And ingreso el texto "Completo Italiano" en el campo "campo_busqueda_youtube"
        #When hago click en "boton_buscar_youtube"
        Then al hacer click en "boton_buscar_youtube" el servicio "https://www.youtube.com/youtubei/v1/search?prettyPrint=false" debe responder en menos de 100 ms
        And espero 3 segundos
