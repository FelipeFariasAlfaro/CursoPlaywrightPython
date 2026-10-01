

from behave import step
from helpers.locator_loader import load_locators
from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

selectores = load_locators()

@step('mi ubicación simulada es latitud {lat:f} y longitud {lon:f}')
def step_impl(context, lat, lon):
    context.browser_context.set_geolocation({"latitude": lat, "longitude": lon})


@step('valido que la geolocalizacion es latitud {lat:f} y longitud {lon:f}')
def step_impl(context, lat, lon):
    # Leemos el texto que la web tiene en pantalla
    texto_lat = context.page.locator(selectores['resultado_latitud']).inner_text()
    texto_lon = context.page.locator(selectores['resultado_longitud']).inner_text()

    # Convertimos a número (float) para poder comparar
    lat_front = float(texto_lat.strip())
    lon_front = float(texto_lon.strip())

    # Comparación con tolerancia (el front puede mostrar más/menos decimales)
    tolerancia = 0.0001
    assert abs(lat_front - lat) < tolerancia, (
        f"Latitud esperada {lat}, en pantalla {lat_front}"
    )
    assert abs(lon_front - lon) < tolerancia, (
        f"Longitud esperada {lon}, en pantalla {lon_front}"
    )
