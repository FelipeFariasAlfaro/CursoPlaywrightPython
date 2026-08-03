Feature: Flujo de compra E2E

  @centyc-e2e
  Scenario: Flujo de compra happy path
    Given ingreso a la página "https://centyc.cl/tiendaqa"
    And hago click en "ver_todos_los_productos" 
    And hago click en "primer_producto" 
