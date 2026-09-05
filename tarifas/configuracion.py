from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


SUPLEMENTOS = {
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
PRECIOS_EXE = [
    71, 75, 80, 85, 95, 110, 90,       # 1–7
    75, 71, 85, 90, 105, 120, 115,     # 8–14
    80, 75, 71, 85, 100, 125, 95,      # 15–21
    71, 80, 90, 75, 110, 130, 100,     # 22–28
]


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
