import logging
import time

from . import configuracion
from .automatizacion import escribir_tarifas
from .calculo import generar_tarifas_diarias
from .entrada import seleccionar_tarifa
from .formato import formatear_precio
from .registros import registrar_resumen


def ejecutar(precios_exe=None, *, controles=None, leer=input, mostrar=print, esperar=time.sleep):
    precios = list(configuracion.PRECIOS_EXE if precios_exe is None else precios_exe)
    if not precios:
        mostrar("No hay días a procesar. Introduce los precios en PRECIOS_EXE de configuracion.py.")
        return
    seleccion = seleccionar_tarifa(leer, mostrar)
    tarifas = generar_tarifas_diarias(seleccion, precios)
    # Comprobar el formato antes de pedir al usuario que enfoque el programa externo.
    for tarifa in tarifas:
        formatear_precio(tarifa)
    registrar_resumen(seleccion, precios, tarifas)
    mostrar(f"En {configuracion.SEGUNDOS_PARA_ENFOCAR} segundos comenzará la escritura. "
            "Enfoca la primera casilla del programa externo. Ctrl+C cancela en la consola.")
    esperar(configuracion.SEGUNDOS_PARA_ENFOCAR)
    escribir_tarifas(tarifas, controles)
    mostrar(f"Escritura completada: {len(tarifas)} días.")


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nOperación cancelada.")
    except (ValueError, ImportError) as error:
        logging.getLogger(__name__).error("No se pudo completar la operación: %s", error)
        return 1
    return 0
