from behave import step
from helpers.auth_manager import AuthManager
import os

@step('ingreso sesión con "{email}" o utilizo la existente')
def step_impl(context, email):
    password = os.getenv("LOGIN_PASSWORD")
    AuthManager(context).ingresar(email, password)