Feature: formulario de centyc

  @formulario1
  Scenario Outline: completar formulario de pruebas
    Given ingreso a la página "https://centyc.cl/practica"
    And hago click en "fc_tab_formulario"
    And ingreso el texto "<nombre>" en el campo "fc_input_nombre"
    And ingreso el texto "<mail>" en el campo "fc_input_email"
    And selecciono en el elemento "fc_tipo_consulta" la opción "<tipo_consulta>"
    And hago click en el color "//label[text()='<color>']"
    And ingreso el texto "<fecha_nac>" en el campo "fc_fecha_nacimiento"
    And ingreso el texto "<asunto>" en el campo "fc_asunto"
    And ingreso el texto "<mensaje>" en el campo "fc_mensaje"
    And espero 5 segundos

  Examples:
    | nombre         | mail                       | tipo_consulta | color  | fecha_nac  | asunto               | mensaje                        |
    | Juan Mendez    | juan.lopez@hotmail.com     | Reclamo       | Rojo   | 1990-03-01 | Mi asunto es hola    | Necesito decirles que...       |
    | Maria Perez    | maria.perezgmail.com       | Consulta      | Azul   | 1985-07-15 | Consulta general     | Quisiera mas informacion       |
    | Pedro Soto     | pedro.soto@outlook.com     | Sugerencia    | Negro  | 1992-11-22 | Sugerencia de mejora | Podrian agregar esta funcion   |
    | Ana Rojas      | ana.rojas@yahoo.com        | Otro          | Blanco |            | Otro tema            | Tengo un tema distinto         |
    | Luis Gonzalez  | luis.gonzalez@hotmail.com  | Reclamo       | Otros  | 1995-09-30 | Reclamo por servicio | El servicio no fue el esperado |
    | Carla Munoz    | carla.munoz@gmail.com      | Consulta      | Rojo   | 2000-04-18 | Consulta de horario  | Cual es el horario de atencion |
    | Diego Torres   | diego.torres@outlook.com   | Sugerencia    | Azul   | 1983-12-12 |                      | Propongo una nueva idea        |
    | Sofia Castro   | sofia.castro@yahoo.com     | Otro          | Negro  | 1998-06-25 | Consulta varia       | Escribo por varios motivos     |
    | Jorge Ramirez  | jorge.ramirez@gmail.com    | Reclamo       | Blanco | 1991-02-08 | Reclamo urgente      | Requiere atencion inmediata    |
    | Valentina Diaz | valentina.diaz@hotmail.com | Consulta      | Otros  | 1996-10-03 | Consulta de producto | Deseo saber mas del producto   |


