from dataclasses import dataclass


SUPLEMENTOS = {
    "EXE": 0,
    "PREMIUM": 30,
    "TRIPLE": 25,
    "SUITE": 50,
}
PRECIO_AD = 12

# Introducir aquí los precios EXE sin desayuno, en orden cronológico.
PRECIOS_EXE = []


@dataclass(frozen=True)
class CampoTarifa:
    tipo_habitacion: str
    personas: int = 0
    desayuno: bool = False


# TODO: definir exclusivamente cuando se conozca el orden real de las casillas.
ORDEN_TARIFAS: list[CampoTarifa] = []

# Espera tras cada TAB; ajustar según el tiempo de respuesta del programa.
PAUSA_ENTRE_CAMPOS = 0.1
