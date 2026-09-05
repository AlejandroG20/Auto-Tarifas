import logging
import time
from typing import Callable, Protocol

from . import configuracion
from .calculo import preparar_dias, validar_importe


logger = logging.getLogger(__name__)


class Controles(Protocol):
    def escribir(self, texto: str) -> None: ...
    def pulsar_tab(self) -> None: ...
    def pausar(self, segundos: float) -> None: ...


class ControlesPyAutoGUI:
    """Adaptador sustituible por los auxiliares de una futura interfaz."""

    def __init__(self):
        import pyautogui

        self._pyautogui = pyautogui

    def escribir(self, texto: str) -> None:
        self._pyautogui.write(texto)

    def pulsar_tab(self) -> None:
        self._pyautogui.press("tab")

    def pausar(self, segundos: float) -> None:
        time.sleep(segundos)


def escribir_tarifas(tarifas, controles: Controles | None = None, *, pausa=None,
                     separador_decimal=".") -> None:
    """Escribe desde la casilla enfocada. Incluye TAB tras la última tarifa."""
    if separador_decimal not in (".", ","):
        raise ValueError("El separador decimal debe ser '.' o ','.")
    espera = validar_importe(
        configuracion.PAUSA_ENTRE_CAMPOS if pausa is None else pausa,
        "Pausa entre campos", permitir_cero=True,
    )
    # Materializar y validar todo antes de emitir la primera pulsación.
    textos = [
        format(validar_importe(tarifa, "Tarifa"), "f").replace(".", separador_decimal)
        for tarifa in tarifas
    ]
    if not textos:
        return
    controles = controles if controles is not None else ControlesPyAutoGUI()
    for texto in textos:
        controles.escribir(texto)
        controles.pulsar_tab()
        controles.pausar(float(espera))


def procesar_dias(precios_exe=None, orden=None, *, controles: Controles | None = None,
                  cambiar_dia: Callable[[int], None] | None = None,
                  pausa=None, separador_decimal=".") -> None:
    """cambiar_dia recibe el número del próximo día (desde 2) y enfoca su primera casilla."""
    dias = preparar_dias(precios_exe, orden)
    if cambiar_dia is not None and not callable(cambiar_dia):
        raise ValueError("cambiar_dia debe ser una función.")
    if len(dias) > 1 and cambiar_dia is None:
        raise ValueError("Falta definir la navegación entre días mediante cambiar_dia.")
    for dia in dias:
        if dia.numero > 1:
            cambiar_dia(dia.numero)
        logger.info("DÍA %s | EXE BASE: %s €", dia.numero, format(dia.precio_exe, "f"))
        logger.debug("Tarifas del día %s: %s", dia.numero, dia.tarifas)
        escribir_tarifas(dia.tarifas, controles, pausa=pausa,
                         separador_decimal=separador_decimal)
