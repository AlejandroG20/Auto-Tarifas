from . import configuracion
from .configuracion import CampoTarifa


def _elegir(titulo, opciones, leer, mostrar):
    mostrar("\n" + titulo)
    for numero, opcion in enumerate(opciones, start=1):
        mostrar(f"{numero}. {opcion}")
    while True:
        respuesta = leer("Selecciona una opción: ").strip()
        if respuesta in {str(i) for i in range(1, len(opciones) + 1)}:
            return int(respuesta) - 1
        mostrar(f"Opción no válida. Introduce un número del 1 al {len(opciones)}.")


def seleccionar_tarifa(leer=input, mostrar=print) -> CampoTarifa:
    habitaciones = tuple(configuracion.OCUPACIONES)
    tipo = habitaciones[_elegir("TIPO DE HABITACIÓN", habitaciones, leer, mostrar)]
    desayuno = _elegir("¿INCLUYE DESAYUNO?", ("Sí", "No"), leer, mostrar) == 0
    porcentaje = configuracion.DESCUENTO_NO_REEMBOLSABLE * 100
    no_reembolsable = _elegir(
        "TIPO DE TARIFA", ("Estándar", f"No reembolsable (-{porcentaje:g} %)"),
        leer, mostrar,
    ) == 1
    return CampoTarifa(tipo, desayuno=desayuno, no_reembolsable=no_reembolsable)


def seleccionar_mes(leer=input, mostrar=print) -> str:
    meses = tuple(configuracion.PRECIOS_2027)
    if not meses:
        raise ValueError("PRECIOS_2027 no contiene meses.")
    return meses[_elegir("MES", meses, leer, mostrar)]


def seleccionar_flujo(leer=input, mostrar=print) -> str:
    opciones = ("FNS", "Mirai")
    return opciones[_elegir("PROGRAMA", opciones, leer, mostrar)]


def seleccionar_bimestre(leer=input, mostrar=print) -> tuple[str, str]:
    bimestres = configuracion.BIMESTRES_MIRAI
    return bimestres[_elegir(
        "BIMESTRE", tuple(f"{a} - {b}" for a, b in bimestres), leer, mostrar,
    )]


def seleccionar_habitacion_mirai(leer=input, mostrar=print) -> str:
    habitaciones = tuple(configuracion.OCUPACIONES_MIRAI)
    return habitaciones[_elegir("HABITACION MIRAI", habitaciones, leer, mostrar)]
