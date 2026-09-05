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
