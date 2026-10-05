import unittest
from decimal import Decimal
from unittest.mock import Mock, call, patch

from tarifas.calculo import calcular_precio, generar_tarifas_diarias
from tarifas.configuracion import CampoTarifa
from tarifas.consola import ejecutar
from tarifas.entrada import seleccionar_tarifa
from tarifas.formato import formatear_precio


class SeleccionTests(unittest.TestCase):
    def test_no_reembolsable(self):
        self.assertEqual(calcular_precio(90, "EXE", no_reembolsable=True), Decimal("85.50"))
        self.assertEqual(calcular_precio(90, "PREMIUM", desayuno=True, huespedes=2,
                                        no_reembolsable=True), Decimal("136.80"))

    def test_redondeo_al_final_half_up(self):
        for base, nr, esperado in [("90.10", True, "85.60"), ("90.005", False, "90.01"),
                                   ("90.014", True, "85.51")]:
            self.assertEqual(str(calcular_precio(Decimal(base), "EXE", no_reembolsable=nr)), esperado)

    def test_huespedes_invalidos(self):
        for numero in [0, -1, Decimal("1.5"), True, "2"]:
            with self.subTest(numero=numero), self.assertRaises(ValueError):
                calcular_precio(90, "EXE", desayuno=True, huespedes=numero)
        with self.assertRaises(ValueError):
            calcular_precio(90, "EXE", huespedes=-1)
        self.assertEqual(calcular_precio(90, "EXE", huespedes=3), Decimal("90.00"))

    def test_modalidad_invalida(self):
        for modalidad in [0, 1, "NO REEMBOLSABLE", None]:
            with self.subTest(modalidad=modalidad), self.assertRaises(ValueError):
                calcular_precio(90, "EXE", no_reembolsable=modalidad)

    def test_descuento_configurable(self):
        with patch("tarifas.configuracion.DESCUENTO_NO_REEMBOLSABLE", Decimal("0.10")):
            self.assertEqual(calcular_precio(100, "EXE", no_reembolsable=True), 90)
        for descuento in [Decimal("-0.1"), Decimal("1"), Decimal("NaN")]:
            with patch("tarifas.configuracion.DESCUENTO_NO_REEMBOLSABLE", descuento):
                with self.assertRaises(ValueError):
                    calcular_precio(90, "EXE", no_reembolsable=True)

    def test_array_diario(self):
        with patch("tarifas.configuracion.PRECIOS_EXE", [90, 100, 110]):
            self.assertEqual(generar_tarifas_diarias(CampoTarifa("PREMIUM", 2, True, True)),
                             [Decimal("136.80"), Decimal("146.30"), Decimal("155.80")])
        self.assertEqual(generar_tarifas_diarias(CampoTarifa("EXE"), [100, 90, 100]), [100, 90, 100])

    def test_entrada_reintenta(self):
        leer = Mock(side_effect=["x", "6", "3", "0", "1", "3", "2"])
        self.assertEqual(seleccionar_tarifa(leer, Mock()), CampoTarifa("PREMIUM", desayuno=True, no_reembolsable=True))
        self.assertEqual(leer.call_count, 7)

    def test_sin_desayuno_no_pide_huespedes(self):
        leer = Mock(side_effect=["1", "2", "1"])
        self.assertEqual(seleccionar_tarifa(leer, Mock()), CampoTarifa("INDIVIDUAL"))
        self.assertEqual(leer.call_count, 3)

    def test_formato_centralizado(self):
        self.assertEqual(formatear_precio(Decimal("136.8")), "136.80")
        with patch("tarifas.configuracion.SEPARADOR_DECIMAL", ","):
            self.assertEqual(formatear_precio(Decimal("136.8")), "136,80")
        with self.assertRaises(ValueError):
            formatear_precio(Decimal("0.001"))

    def test_consola_resumen_circuito(self):
        controles, esperar, leer = Mock(), Mock(), Mock(side_effect=["1", "2"])
        with self.assertLogs("tarifas.registros", level="INFO") as logs:
            ejecutar([90, 100, 110], controles=controles, leer=leer,
                     mostrar=Mock(), esperar=esperar)
        self.assertEqual(leer.call_count, 2)
        esperar.assert_called_once()
        self.assertEqual(controles.escribir.call_count, 144)
        self.assertIn("DÍAS A PROCESAR: 3", logs.output[0])
        self.assertIn("FILAS: 48", logs.output[0])
        self.assertIn("TARIFA FINAL: 90.00", logs.output[2])

    def test_dia_invalido_no_escribe(self):
        controles, esperar = Mock(), Mock()
        with self.assertRaises(ValueError):
            ejecutar([90, -1], controles=controles, leer=Mock(side_effect=["1", "2"]),
                     mostrar=Mock(), esperar=esperar)
        self.assertEqual(controles.mock_calls, [])
        esperar.assert_not_called()

    def test_array_vacio_no_pregunta_ni_escribe(self):
        controles, leer, esperar = Mock(), Mock(), Mock()
        ejecutar([], controles=controles, leer=leer, mostrar=Mock(), esperar=esperar)
        leer.assert_not_called()
        esperar.assert_not_called()
        self.assertEqual(controles.mock_calls, [])
