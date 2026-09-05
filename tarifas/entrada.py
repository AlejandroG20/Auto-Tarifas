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
    habitaciones = tuple(configuracion.SUPLEMENTOS)
    tipo = habitaciones[_elegir("TIPO DE HABITACIÓN", habitaciones, leer, mostrar)]
    desayuno = _elegir("¿INCLUYE DESAYUNO?", ("Sí", "No"), leer, mostrar) == 0
    huespedes = 0
    if desayuno:
        while True:
            try:
                huespedes = int(leer("Número de huéspedes: ").strip())
                if huespedes >= 1:
                    break
            except ValueError:
                pass
            mostrar("Introduce un número entero de huéspedes mayor o igual que 1.")
    porcentaje = configuracion.DESCUENTO_NO_REEMBOLSABLE * 100
    no_reembolsable = _elegir(
        "TIPO DE TARIFA", ("Reembolsable", f"No reembolsable (-{porcentaje:g} %)"),
        leer, mostrar,
    ) == 1
    return CampoTarifa(tipo, huespedes, desayuno, no_reembolsable)
