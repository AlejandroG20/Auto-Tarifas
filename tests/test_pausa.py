import threading
import unittest
from unittest.mock import Mock, patch

from tarifas.automatizacion import escribir_tarifas
from tarifas.pausa import PausaEscritura


class PausaTests(unittest.TestCase):
    def test_pulsacion_mantenida_y_reanudacion(self):
        pausa = PausaEscritura()
        pausa.actualizar(True)
        pausa.actualizar(True)
        self.assertFalse(pausa._continuar.is_set())
        pausa.actualizar(False)
        pausa.actualizar(True)
        self.assertTrue(pausa._continuar.is_set())

    def test_bloquea_hasta_reanudar(self):
        pausa = PausaEscritura()
        pausa.actualizar(True)
        terminado = threading.Event()
        hilo = threading.Thread(target=lambda: (pausa.esperar(), terminado.set()))
        hilo.start()
        try:
            self.assertFalse(terminado.wait(0.1))
            pausa.actualizar(False)
            pausa.actualizar(True)
            self.assertTrue(terminado.wait(1))
        finally:
            pausa._continuar.set()
            hilo.join(1)

    def test_pausa_entre_casillas_y_limpieza_si_falla(self):
        eventos = Mock()
        pausa = eventos.pausa
        pausa.activar.return_value.__enter__ = Mock()
        pausa.activar.return_value.__exit__ = Mock(return_value=False)
        with patch("tarifas.automatizacion.PausaEscritura", return_value=pausa), \
             patch("tarifas.automatizacion.ControlesPyAutoGUI", return_value=eventos.controles):
            escribir_tarifas([90, 95], pausa=0)
        from unittest.mock import call
        acciones = [c for c in eventos.mock_calls
                    if c[0] in ("pausa.esperar", "controles.escribir", "controles.pulsar_tab")]
        self.assertEqual(acciones, [
            call.pausa.esperar(), call.controles.escribir("90.00"), call.controles.pulsar_tab(),
            call.pausa.esperar(), call.controles.escribir("95.00"), call.controles.pulsar_tab(),
        ])
        pausa.activar.return_value.__exit__.assert_called_once()
        pausa.activar.return_value.__exit__.reset_mock()
        eventos.controles.escribir.side_effect = KeyboardInterrupt
        with patch("tarifas.automatizacion.PausaEscritura", return_value=pausa), \
             patch("tarifas.automatizacion.ControlesPyAutoGUI", return_value=eventos.controles):
            with self.assertRaises(KeyboardInterrupt):
                escribir_tarifas([90])
        pausa.activar.return_value.__exit__.assert_called_once()
