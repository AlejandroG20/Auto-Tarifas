from dataclasses import dataclass
from decimal import Decimal
from numbers import Real
from typing import Iterable

from . import configuracion
from .configuracion import CampoTarifa


def validar_importe(valor, nombre: str, *, permitir_cero: bool = False) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, (Real, Decimal)):
        raise ValueError(f"{nombre} debe ser numérico.")
    importe = Decimal(str(valor))
    if not importe.is_finite() or importe < 0 or (importe == 0 and not permitir_cero):
        condicion = "mayor o igual que 0" if permitir_cero else "mayor que 0"
        raise ValueError(f"{nombre} debe ser finito y {condicion}.")
    return importe


def validar_seleccion(tipo_habitacion, personas, desayuno, no_reembolsable):
    if not isinstance(tipo_habitacion, str) or tipo_habitacion not in configuracion.SUPLEMENTOS:
        raise ValueError(f"Tipo de habitación no válido: {tipo_habitacion!r}.")
    if isinstance(personas, bool) or not isinstance(personas, int) or personas < 0:
        raise ValueError("El número de personas debe ser un entero mayor o igual que 0.")
    if not isinstance(desayuno, bool):
        raise ValueError("Desayuno debe ser un booleano.")
    if desayuno and personas < 1:
        raise ValueError("Con desayuno debe haber al menos 1 huésped.")
    if not isinstance(no_reembolsable, bool):
        raise ValueError("La modalidad no_reembolsable debe ser un booleano.")


def redondear_importe(importe: Decimal) -> Decimal:
    return importe.quantize(configuracion.UNIDAD_MONETARIA,
                            rounding=configuracion.REDONDEO_MONETARIO)


def calcular_precio(precio_exe, tipo_habitacion, personas=0, desayuno=False,
                    no_reembolsable=False, *, huespedes=None) -> Decimal:
    # Mantener las llamadas posicionales y el nombre personas de la primera fase.
    if huespedes is not None:
        if personas != 0:
            raise ValueError("Utiliza solo personas o huespedes, no ambos.")
        personas = huespedes
    base = validar_importe(precio_exe, "Precio EXE")
    validar_seleccion(tipo_habitacion, personas, desayuno, no_reembolsable)
    suplemento = validar_importe(
        configuracion.SUPLEMENTOS[tipo_habitacion], "Suplemento", permitir_cero=True
    )
    precio_ad = validar_importe(configuracion.PRECIO_AD, "Precio AD", permitir_cero=True)
    precio = base + suplemento + (precio_ad * personas if desayuno else Decimal(0))
    if no_reembolsable:
        descuento = validar_importe(configuracion.DESCUENTO_NO_REEMBOLSABLE,
                                    "Descuento no reembolsable", permitir_cero=True)
        if descuento >= 1:
            raise ValueError("El descuento debe ser menor que 1.")
        precio *= Decimal(1) - descuento
    return redondear_importe(precio)


def resolver_orden(orden=None) -> tuple[CampoTarifa, ...]:
    campos = tuple(configuracion.ORDEN_TARIFAS if orden is None else orden)
    if not campos:
        raise ValueError("ORDEN_TARIFAS está vacío: falta definir el orden real de las casillas.")
    if any(not isinstance(campo, CampoTarifa) for campo in campos):
        raise ValueError("Cada entrada del orden debe ser un CampoTarifa.")
    return campos


def generar_tarifas_dia(precio_exe, orden=None) -> tuple[Decimal, ...]:
    return tuple(
        calcular_precio(precio_exe, campo.tipo_habitacion, campo.personas,
                        campo.desayuno, campo.no_reembolsable)
        for campo in resolver_orden(orden)
    )


@dataclass(frozen=True)
class TarifasDia:
    numero: int
    precio_exe: Decimal
    tarifas: tuple[Decimal, ...]


def preparar_dias(precios_exe: Iterable | None = None, orden=None) -> tuple[TarifasDia, ...]:
    """Valida todos los días antes de permitir cualquier escritura externa."""
    campos = resolver_orden(orden)
    precios = configuracion.PRECIOS_EXE if precios_exe is None else precios_exe
    return tuple(
        TarifasDia(numero, validar_importe(base, "Precio EXE"), generar_tarifas_dia(base, campos))
        for numero, base in enumerate(precios, start=1)
    )


def generar_tarifas_diarias(seleccion: CampoTarifa, precios_exe=None) -> list[Decimal]:
    """Aplica una única combinación a todos los días, sin depender de ORDEN_TARIFAS."""
    if not isinstance(seleccion, CampoTarifa):
        raise ValueError("La selección debe ser un CampoTarifa.")
    validar_seleccion(seleccion.tipo_habitacion, seleccion.personas,
                      seleccion.desayuno, seleccion.no_reembolsable)
    return [dia.tarifas[0] for dia in preparar_dias(precios_exe, [seleccion])]
