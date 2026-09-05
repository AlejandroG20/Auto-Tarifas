from . import configuracion
from .calculo import redondear_importe, validar_importe


def formatear_precio(precio, separador_decimal=None) -> str:
    separador = (configuracion.SEPARADOR_DECIMAL if separador_decimal is None
                 else separador_decimal)
    if separador not in (".", ","):
        raise ValueError("El separador decimal debe ser '.' o ','.")
    importe = redondear_importe(validar_importe(precio, "Tarifa"))
    if importe <= 0:
        raise ValueError("La tarifa redondeada debe ser mayor que 0.")
    return format(importe, ".2f").replace(".", separador)
