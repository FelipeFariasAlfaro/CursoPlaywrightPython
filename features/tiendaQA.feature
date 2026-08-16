Feature: Flujo de compra E2E

  @centyc-e2e
  Scenario: Flujo de compra happy path
    Given ingreso a la página "https://centyc.cl/tiendaqa"
    And hago click en "ver_todos_los_productos" 
    And hago click en "primer_producto"
    And presiono el elemento "btn_incrementar" un numero de 3 veces
    And hago click en "add_al_carrito"
    And hago click en "ver_carrito"
    And hago click en "ir_al_pago"
    And ingreso el texto "Felipe" en el campo "input_nombre"
    And ingreso el texto "Farias" en el campo "input_apellido"
    And ingreso "felipe.farias@centyc.cl" en el campo "input_mail" con delay de 300 ms
    And ingreso "+5556666677" en el campo "input_fono" con delay de 100 ms
    And hago click en "btn_continuar_pago"
    And ingreso el texto "Avenida siempre viva 123" en el campo "input_direccion"
    And ingreso el texto "Springfield" en el campo "input_ciudad"
    And ingreso el texto "Los Lagos" en el campo "input_region"
    And ingreso el texto "555677" en el campo "codigo_postal"
    And hago click en "envio_express"
    And hago click en "continua_a_pago"
    And ingreso el texto "Juan Perez" en el campo "nombre_tarjeta"
    And ingreso el texto "1234567812340000" en el campo "numero_tarjeta"
    And ingreso el texto "12/35" en el campo "vencimiento_tarjeta"
    And ingreso el texto "987" en el campo "ccv_tarjeta"
    And hago click en "boton_confirmar_perdido"
    And espero 2 segundos
    Then el texto "Gracias por tu compra, Felipe." debe estar visible en pantalla
    And el elemento "titulo_confirmado" debe contener el texto "¡Pedido confirmado!"
    And el elemento "btn_seguir_comprando" debe ser visible en la pagina




    
    


    
    
    

    



    
