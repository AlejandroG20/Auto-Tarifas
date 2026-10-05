from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


OCUPACIONES = {
    "INDIVIDUAL": [1],
    "DOBLE_EXECUTIVE": [1, 2],
    "PREMIUM": [1, 2],
    "TRIPLE": [1, 2, 3],
    "SUITE": [1, 2, 3, 4],
}

# Orden de las habitaciones y bloques mostrado por el programa externo.
ORDEN_HABITACIONES = (
    "INDIVIDUAL", "DOBLE_EXECUTIVE", "PREMIUM", "SUITE", "TRIPLE",
)
# (nombre, desayuno, no_reembolsable)
MODALIDADES = (
    ("TARIFA ESTÁNDAR", False, False),
    ("OFERTA NO REEMBOLSABLE", False, True),
    ("NO REEMBOLSABLE HD", True, True),
    ("ALOJAMIENTO CON DESAYUNO INCLUIDO", True, False),
)

SUPLEMENTOS = {
    "INDIVIDUAL": 0,
    "DOBLE_EXECUTIVE": 0,
    "EXE": 0,
    "PREMIUM": 30,
    "TRIPLE": 25,
    "SUITE": 50,
}
PRECIO_AD = 12
DESCUENTO_NO_REEMBOLSABLE = Decimal("0.05")
UNIDAD_MONETARIA = Decimal("0.01")
REDONDEO_MONETARIO = ROUND_HALF_UP
SEPARADOR_DECIMAL = "."
SEGUNDOS_PARA_ENFOCAR = 5

# Precios EXE sin desayuno, reembolsables, en orden cronológico.
# Usar enteros o Decimal("90.50") para los importes con céntimos.
PRECIOS_2027 = {
    "enero": [
        71, 71, 71, 71, 71, 71, 71,
        500, 500, 500, 500, 500, 500, 500,
        500, 500, 500, 500, 500, 500, 500,
        500, 500, 500, 500, 500, 500, 500,
        500, 500, 500
    ],

    "febrero": [
        500, 75, 75, 75, 85, 85, 75,
        75, 75, 75, 75, 75, 500, 85,
        75, 75, 75, 75, 75, 85, 85,
        75, 75, 75, 75, 75, 85, 85
    ],

    "marzo": [
        85, 85, 85, 85, 95, 95, 85,
        85, 85, 85, 85, 95, 95, 85,
        85, 85, 85, 85, 95, 95, 85,
        85, 85, 85, 130, 130, 130, 130,
        95, 85, 85
    ],

    "abril": [
        91, 101, 101, 95, 95, 95, 95,
        95, 101, 101, 95, 95, 95, 95,
        95, 101, 101, 95, 95, 95, 95,
        95, 101, 101, 95, 95, 95, 95,
        95, 130
    ],

    "mayo": [
        130, 130, 97, 97, 97, 97, 107,
        107, 97, 97, 97, 97, 97, 107,
        107, 97, 97, 97, 97, 97, 107,
        107, 97, 97, 97, 97, 97, 107,
        107, 97, 97
    ],

    "junio": [
        113, 113, 113, 113, 113, 99, 99,
        99, 99, 99, 113, 113, 99, 99,
        99, 99, 99, 113, 113, 99, 99,
        99, 99, 99, 113, 113, 99, 99,
        99, 99
    ],

    "julio": [
        117, 117, 117, 113, 113, 113, 113,
        113, 117, 117, 113, 113, 113, 113,
        113, 117, 117, 113, 113, 113, 113,
        113, 117, 117, 113, 113, 113, 113,
        113, 117, 117
    ],

    "agosto": [
        115, 115, 115, 115, 115, 125, 125,
        115, 130, 130, 130, 130, 130, 130,
        130, 130, 130, 130, 115, 125, 125,
        115, 115, 115, 115, 115, 125, 125,
        115, 115, 115
    ],

    "septiembre": [
        113, 113, 117, 117, 113, 113, 113,
        113, 113, 117, 117, 113, 113, 113,
        113, 113, 117, 117, 113, 113, 113,
        113, 113, 117, 117, 113, 113, 113,
        113, 113
    ],

    "octubre": [
        113, 113, 99, 99, 99, 99, 99,
        113, 113, 113, 113, 113, 99, 99,
        113, 113, 99, 99, 99, 99, 99,
        113, 113, 99, 99, 99, 99, 99,
        113, 113, 99
    ],

    "noviembre": [
        113, 79, 79, 79, 89, 89, 79,
        79, 79, 79, 79, 89, 89, 79,
        79, 79, 79, 79, 89, 89, 79,
        79, 79, 79, 79, 89, 89, 79,
        79, 79
    ],

    "diciembre": [
        113, 113, 113, 113, 113, 113, 113,
        113, 69, 75, 75, 69, 69, 69,
        69, 69, 69, 75, 69, 69, 69,
        69, 69, 69, 75, 69, 69, 69,
        69, 69, 500
    ],
}

PRECIOS_EXE = PRECIOS_2027["febrero"]

@dataclass(frozen=True)
class CampoTarifa:
    tipo_habitacion: str
    personas: int = 0
    desayuno: bool = False
    no_reembolsable: bool = False


# TODO: definir exclusivamente cuando se conozca el orden real de las casillas.
ORDEN_TARIFAS: list[CampoTarifa] = []

# Espera tras cada TAB; ajustar según el tiempo de respuesta del programa.
PAUSA_ENTRE_CAMPOS = 0.1
