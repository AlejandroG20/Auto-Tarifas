import logging
import time

from . import configuracion
from .automatizacion import escribir_tarifas
from .calculo import (generar_circuito_completo, generar_circuito_mirai,
                      obtener_precios_mes, obtener_precios_bimestre)
from .entrada import (seleccionar_mes, seleccionar_flujo, seleccionar_bimestre,
                      seleccionar_habitacion_mirai)
from .formato import formatear_precio
from .registros import registrar_resumen_circuito


def ejecutar(precios_exe=None, *, controles=None, leer=input, mostrar=print, esperar=time.sleep):
    if precios_exe is not None:
        precios_exe = tuple(precios_exe)
        if not precios_exe:
            mostrar("No hay dias a procesar.")
            return
    flujo = seleccionar_flujo(leer, mostrar)
    if flujo == "Mirai":
        bimestre = seleccionar_bimestre(leer, mostrar)
        mes = " - ".join(bimestre)
        precios = obtener_precios_bimestre(bimestre) if precios_exe is None else precios_exe
        generar = generar_circuito_mirai
        inicio = "el dia 1 de EXE, BAR, Solo Alojamiento, ocupacion 2 + 0"
        separador = configuracion.SEPARADOR_DECIMAL_MIRAI
    else:
        mes = seleccionar_mes(leer, mostrar)
        precios = obtener_precios_mes(mes) if precios_exe is None else precios_exe
        generar = generar_circuito_completo
        inicio = "el dia 1 de Individual, tarifa estandar, 1 Pax"
        separador = configuracion.SEPARADOR_DECIMAL
    mostrar(f"PROGRAMA: {flujo} | PERIODO: {mes} (2027)")
    if not precios:
        mostrar(f"No hay dias a procesar en {mes}.")
        return
    filas = generar(precios)
    if flujo == "Mirai":
        habitacion = seleccionar_habitacion_mirai(leer, mostrar)
        filas = tuple(fila for fila in filas if fila.seleccion.tipo_habitacion == habitacion)
        adultos, menores = filas[0].ocupacion
        inicio = (f"el dia 1 de {habitacion}, BAR, Solo Alojamiento, "
                  f"ocupacion {adultos} + {menores}")
        mostrar(f"HABITACION: {habitacion}")
    tarifas = [tarifa for fila in filas for tarifa in fila.tarifas]
    # Comprobar el formato antes de pedir al usuario que enfoque el programa externo.
    for tarifa in tarifas:
        formatear_precio(tarifa, separador)
    registrar_resumen_circuito(mes, precios, filas)
    mostrar(f"En {configuracion.SEGUNDOS_PARA_ENFOCAR} segundos comenzará la escritura. "
            f"Enfoca {inicio}. F8 pausa/reanuda. Ctrl+C cancela en la consola.")
    esperar(configuracion.SEGUNDOS_PARA_ENFOCAR)
    escribir_tarifas(tarifas, controles, separador_decimal=separador)
    mostrar(f"Escritura completada: {len(precios)} días, {len(filas)} filas, "
            f"{len(tarifas)} precios.")


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
