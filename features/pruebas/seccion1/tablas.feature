Feature: Pruebas con tablas

  #sesion_23 en git  
  @tabla_paises  
  Scenario: Prueba validando países 
    Given ingreso a la página "https://centyc.cl/practica"
    When hago click en "seccion_tablas"
    Then valido que los elementos de la columna "Países" con localizador "columna_paises" son correctos
            | Países        |
            | Argentina     |
            | Chile         |
            | Colombia      |
            | España        |
            | Francia       |
            | Japón         |
            | Korea del Sur |

