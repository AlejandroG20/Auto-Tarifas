import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

from tarifas.automatizacion import escribir_tarifas, procesar_dias
from tarifas.calculo import calcular_precio, preparar_dias
from tarifas.configuracion import CampoTarifa


class TarifasTests(unittest.TestCase):
    def test_ejemplos(self):
        for tipo, personas, ad, esperado in [
            ("EXE", 0, False, 90), ("PREMIUM", 0, False, 120),
            ("TRIPLE", 0, False, 115), ("SUITE", 0, False, 140),
            ("EXE", 1, True, 102), ("EXE", 2, True, 114),
            ("PREMIUM", 2, True, 144), ("TRIPLE", 3, True, 151),
            ("SUITE", 2, True, 164),
        ]:
            with self.subTest(tipo=tipo, personas=personas, ad=ad):
                self.assertEqual(calcular_precio(90, tipo, personas, ad), esperado)

    def test_ocupacion_y_decimales(self):
        self.assertEqual(calcular_precio(90.15, "EXE", 3), Decimal("90.15"))
        self.assertEqual(calcular_precio(90.15, "EXE", 2, True), Decimal("114.15"))

    def test_validaciones(self):
        for valor in [0, -1, "90", True, None, float("nan"), float("inf")]:
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                calcular_precio(valor, "EXE")
        for personas in [-1, 1.5, True, "2"]:
            with self.subTest(personas=personas), self.assertRaises(ValueError):
                calcular_precio(90, "EXE", personas)
        with self.assertRaises(ValueError):
            calcular_precio(90, "OTRA")
        with self.assertRaises(ValueError):
            calcular_precio(90, "EXE", desayuno="sí")

    def test_configuracion_dinamica(self):
        with patch("tarifas.configuracion.PRECIO_AD", 15):
            self.assertEqual(calcular_precio(90, "EXE", 2, True), 120)

    def test_orden_y_dias_se_conservan(self):
        # Orden sintético para verificar la API; no representa las casillas reales.
        orden = [CampoTarifa("SUITE", 2, True), CampoTarifa("EXE"), CampoTarifa("EXE")]
        dias = preparar_dias([95, 90, 100], orden)
        self.assertEqual([dia.precio_exe for dia in dias], [95, 90, 100])
        self.assertEqual(dias[0].tarifas, (169, 95, 95))
        self.assertEqual([dia.numero for dia in dias], [1, 2, 3])

    def test_sin_orden_o_navegacion_no_hay_pulsaciones(self):
        controles = Mock()
        with self.assertRaisesRegex(ValueError, "ORDEN_TARIFAS"):
            procesar_dias([90], controles=controles)
        with self.assertRaisesRegex(ValueError, "navegación"):
            procesar_dias([90, 95], [CampoTarifa("EXE")], controles=controles)
        self.assertEqual(controles.mock_calls, [])

    def test_error_en_ultimo_dia_no_escribe_primero(self):
        controles = Mock()
        navegar = Mock()
        with self.assertRaises(ValueError):
            procesar_dias([90, -1], [CampoTarifa("EXE")], controles=controles,
                          cambiar_dia=navegar)
        self.assertEqual(controles.mock_calls, [])
        navegar.assert_not_called()

    def test_secuencia_escritura(self):
        eventos = Mock()
        procesar_dias([90, 95], [CampoTarifa("EXE")], controles=eventos,
                      cambiar_dia=eventos.navegar, pausa=0)
        from unittest.mock import call
        self.assertEqual(eventos.mock_calls, [
            call.escribir("90"), call.pulsar_tab(), call.pausar(0.0),
            call.navegar(2), call.escribir("95"), call.pulsar_tab(), call.pausar(0.0),
        ])

    def test_escritura_valida_toda_la_lista(self):
        controles = Mock()
        with self.assertRaises(ValueError):
            escribir_tarifas([90, -1], controles)
        self.assertEqual(controles.mock_calls, [])
        escribir_tarifas([Decimal("90.25")], controles, separador_decimal=",")
        controles.escribir.assert_called_once_with("90,25")


if __name__ == "__main__":
    unittest.main()
