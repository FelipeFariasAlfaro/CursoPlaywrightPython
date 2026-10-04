@api @todas_las_apis
Feature: Pruebas de API REST con JSONPlaceholder
    JSONPlaceholder es una API pública de pruebas (https://jsonplaceholder.typicode.com).
    
    @api_get
    Scenario: GET - obtener un TODO y validar status, estructura, tipos y valores
        Given que uso la API configurada por defecto
        When hago una peticion GET a "/todos/1"
        Then el status de la respuesta es 200
        And la respuesta tiene los campos
            | campo     |
            | userId    |
            | id        |
            | title     |
            | completed |
        And el campo "id" es de tipo "int"
        And el campo "title" es de tipo "str"
        And el campo "completed" es de tipo "bool"
        And el campo "id" vale el numero 1
        And cierro la conexion de la API

    @api_get_lista
    Scenario: GET - obtener una lista y validar un elemento anidado
        Given que uso la API configurada por defecto
        When hago una peticion GET a "/users"
        Then el status de la respuesta es 200
        And el campo "0.id" es de tipo "int"
        And el campo "0.address.geo.lat" es de tipo "str"
        And el campo "0.company.name" vale "Romaguera-Crona"
        And cierro la conexion de la API

    @api_post
    Scenario: POST - crear un recurso nuevo
        Given que uso la API base "https://jsonplaceholder.typicode.com"
        When hago una peticion POST a "/posts" con el cuerpo
            """
            {
                "title": "Curso Playwright",
                "body": "Prueba de creacion",
                "userId": 7
            }
            """
        Then el status de la respuesta es 201
        And el campo "title" vale "Curso Playwright"
        And el campo "userId" vale el numero 7
        And el campo "id" es de tipo "int"
        And cierro la conexion de la API

    @api_put
    Scenario: PUT - reemplazar un recurso completo
        Given que uso la API configurada por defecto
        When hago una peticion PUT a "/posts/1" con el cuerpo
            """
            {
                "id": 1,
                "title": "Titulo reemplazado",
                "body": "Contenido nuevo",
                "userId": 1
            }
            """
        Then el status de la respuesta es 200
        And el campo "title" vale "Titulo reemplazado"
        And cierro la conexion de la API

    @api_patch
    Scenario: PATCH - actualizar parcialmente un recurso
        Given que uso la API configurada por defecto
        When hago una peticion PATCH a "/posts/1" con el cuerpo
            """
            {
                "title": "Solo cambio el titulo"
            }
            """
        Then el status de la respuesta es 200
        And el campo "title" vale "Solo cambio el titulo"
        And cierro la conexion de la API

    @api_delete
    Scenario: DELETE - eliminar un recurso
        Given que uso la API configurada por defecto
        When hago una peticion DELETE a "/posts/1"
        Then el status de la respuesta es 200
        And cierro la conexion de la API

    @api_headers
    Scenario: Headers - enviar un header de autorizacion
        Given que uso la API configurada por defecto
        And agrego el header "Authorization" con valor "Bearer token-de-prueba-123"
        When hago una peticion GET a "/todos/2"
        Then el status de la respuesta es 200
        And el campo "id" vale el numero 2
        And cierro la conexion de la API
