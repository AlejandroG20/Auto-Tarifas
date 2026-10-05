import logging

from . import configuracion


logger = logging.getLogger(__name__)


def registrar_resumen(seleccion, precios, tarifas):
    descuento = configuracion.DESCUENTO_NO_REEMBOLSABLE * 100 if seleccion.no_reembolsable else 0
    logger.info(
        "CONFIGURACIÓN DE TARIFA\nHabitación: %s\nDesayuno: %s\nHuéspedes: %s\n"
        "Modalidad: %s\nDescuento: %s %%\n\nDÍAS A PROCESAR: %s",
        seleccion.tipo_habitacion, "Sí" if seleccion.desayuno else "No",
        seleccion.personas if seleccion.desayuno else 0,
        "NO REEMBOLSABLE" if seleccion.no_reembolsable else "REEMBOLSABLE",
        format(descuento, "g"), len(tarifas),
    )
    for numero, (base, tarifa) in enumerate(zip(precios, tarifas), start=1):
        logger.info("DÍA %s | EXE: %s € | TARIFA FINAL: %s €", numero, base, format(tarifa, ".2f"))


def registrar_resumen_filas(mes, seleccion, precios, filas):
    logger.info("MES: %s | HABITACION: %s | DESAYUNO: %s | MODALIDAD: %s | "
                "DÍAS A PROCESAR: %s | OCUPACIONES: %s",
                mes, seleccion.tipo_habitacion, "Si" if seleccion.desayuno else "No",
                "NO REEMBOLSABLE" if seleccion.no_reembolsable else "ESTANDAR",
                len(precios), ", ".join(str(fila.personas) for fila in filas))
    for fila in filas:
        for numero, (base, tarifa) in enumerate(zip(precios, fila.tarifas), start=1):
            logger.info("%s Pax | DIA %s | EXE: %s € | TARIFA FINAL: %s €",
                        fila.personas, numero, base, format(tarifa, ".2f"))


def registrar_resumen_circuito(mes, precios, filas):
    logger.info("MES: %s | DÍAS A PROCESAR: %s | FILAS: %s | PRECIOS: %s",
                mes, len(precios), len(filas), sum(len(f.tarifas) for f in filas))
    for fila in filas:
        ocupacion = (f"{fila.ocupacion[0]} + {fila.ocupacion[1]}" if fila.ocupacion
                     else f"{fila.seleccion.personas} Pax")
        logger.info("HABITACIÓN: %s | %s | %s",
                    fila.seleccion.tipo_habitacion, fila.modalidad, ocupacion)
        for numero, (base, tarifa) in enumerate(zip(precios, fila.tarifas), start=1):
            logger.info("DÍA %s | EXE: %s € | TARIFA FINAL: %s €",
                        numero, base, format(tarifa, ".2f"))
