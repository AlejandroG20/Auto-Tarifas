"""Atajo global F8 en Windows, sin dependencias adicionales."""
import ctypes
import logging
import os
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PausaEscritura:
    def __init__(self):
        self._continuar = threading.Event()
        self._continuar.set()
        self._detener = threading.Event()
        self._pulsada = False

    def actualizar(self, pulsada):
        # Una pulsacion mantenida solo cambia el estado una vez.
        if pulsada and not self._pulsada:
            if self._continuar.is_set():
                self._continuar.clear()
                logger.info("EN PAUSA. F8 reanuda la escritura.")
            else:
                self._continuar.set()
                logger.info("Escritura reanudada.")
        self._pulsada = pulsada

    def esperar(self):
        while not self._continuar.wait(0.05):
            pass

    def vigilar(self, leer_tecla):
        while not self._detener.wait(0.02):
            self.actualizar(bool(leer_tecla() & 0x8000))

    @contextmanager
    def activar(self):
        if os.name != "nt":
            raise ValueError("El atajo global F8 requiere Windows.")
        leer = ctypes.WinDLL("user32", use_last_error=True).GetAsyncKeyState
        leer.argtypes = [ctypes.c_int]
        leer.restype = ctypes.c_short
        hilo = threading.Thread(target=self.vigilar, args=(lambda: leer(0x77),),
                                daemon=True)
        hilo.start()
        try:
            yield self
        finally:
            self._detener.set()
            self._continuar.set()
            hilo.join()
