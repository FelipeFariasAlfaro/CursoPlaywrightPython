Feature: Pruebas con archivos


  @prueba_excel1
  Scenario: Subir un documento exitosamente
    Given ingreso a la página "https://centyc.cl/practica"
    And hago click en "tab_archivos"
    When cargo el archivo "historico.xlsx" en el campo de carga "input_archivos"
    And espero 3 segundos
    And hago click en "btn_subir_archivo"
    Then el texto "Se ha cargado correctamente el archivo historico.xlsx" debe estar visible en pantalla