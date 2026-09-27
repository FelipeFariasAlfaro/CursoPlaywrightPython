"""
Soft Asserts para usar DENTRO de un step.

Un soft assert acumula varias verificaciones sin detenerse en el primer fallo,
y al final reporta todos los fallos juntos. Es totalmente autocontenido: no
depende del environment, ni de hooks, ni de tags en el feature.

Uso típico dentro de un step de validaciones:

    from helpers.soft_assert import SoftAssert

    @then(u'valido varias cosas de la página')
    def step_impl(context):
        soft = SoftAssert()

        soft.check(titulo == "Inicio", "El título no es 'Inicio'")
        soft.check(precio > 0, "El precio debería ser positivo")
        soft.check(context.page.locator(sel).is_visible(), "El botón no está visible")

        soft.assert_all()   # <-- si hubo fallos, aquí lanza uno con todos juntos
"""


class SoftAssert:
    """Acumula verificaciones y las reporta todas juntas al final."""

    def __init__(self):
        self.errores = []

    def check(self, condicion, mensaje):
        """Verifica una condición. Si falla, la acumula (no detiene el step)."""
        if not condicion:
            self.errores.append(mensaje)
            print(f"[SOFT ASSERT FALLÓ] {mensaje}")
        return bool(condicion)

    def assert_all(self):
        """
        Evalúa todo lo acumulado. Si hubo al menos un fallo, lanza un
        AssertionError con el listado completo. Si no, no hace nada.
        Llamar al final del step.
        """
        if self.errores:
            lineas = [f"Se acumularon {len(self.errores)} fallo(s):"]
            for i, err in enumerate(self.errores, start=1):
                lineas.append(f"  {i}. {err}")
            raise AssertionError("\n".join(lineas))
