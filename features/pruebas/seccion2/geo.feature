Feature: Pruebas de geolocalización

    @geo1
    Scenario: Pruebas modificando la localización
        Given ingreso a la página "https://centyc.cl/pruebas/elementos-web"
        And hago click en "menu_geo"
        And mi ubicación simulada es latitud 4.6371 y longitud -74.0994    
        When hago click en "btn_obtener_mi_geo"
        Then valido que la geolocalizacion es latitud 4.6371 y longitud -74.0994   