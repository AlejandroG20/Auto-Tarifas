import unittest
from decimal import Decimal
from unittest.mock import Mock, call, patch

from tarifas import configuracion
from tarifas.calculo import generar_circuito_completo
from tarifas.consola import ejecutar


# Orden y cantidades independientes de la configuracion de produccion.
HABITACIONES = [("INDIVIDUAL", 1, 0), ("DOBLE_EXECUTIVE", 2, 0),
                ("PREMIUM", 2, 30), ("SUITE", 4, 50), ("TRIPLE", 3, 25)]
MODALIDADES = [(False, False), (False, True), (True, True), (True, False)]


class CircuitoTests(unittest.TestCase):
    def test_orden_completo_y_calculos(self):
        filas = generar_circuito_completo(iter([90, 100]))
        esperado = [(tipo, pax, ad, nr) for tipo, max_pax, _ in HABITACIONES
                    for ad, nr in MODALIDADES for pax in range(1, max_pax + 1)]
        self.assertEqual([(f.seleccion.tipo_habitacion, f.seleccion.personas,
                           f.seleccion.desayuno, f.seleccion.no_reembolsable)
                          for f in filas], esperado)
        self.assertEqual(len(filas), 48)
        indice = 0
        for tipo, max_pax, suplemento in HABITACIONES:
            for ad, nr in MODALIDADES:
                for pax in range(1, max_pax + 1):
                    precios = tuple((Decimal(base + suplemento + (12 * pax if ad else 0)) *
                                     (Decimal("0.95") if nr else Decimal(1))).quantize(
                                         Decimal("0.01")) for base in [90, 100])
                    self.assertEqual(filas[indice].tarifas, precios)
                    indice += 1

    def test_consola_solo_mes_y_tabs_en_orden(self):
        controles, leer, esperar = Mock(), Mock(side_effect=["1", "2"]), Mock()
        with patch.dict(configuracion.PRECIOS_2027,
                        {"enero": [999], "febrero": [90, 100]}, clear=True), \
             patch("tarifas.automatizacion.ControlesPyAutoGUI", side_effect=AssertionError("GUI real")):
            ejecutar(controles=controles, leer=leer, mostrar=Mock(), esperar=esperar)
        self.assertEqual(leer.call_count, 2)
        esperar.assert_called_once_with(configuracion.SEGUNDOS_PARA_ENFOCAR)
        # Cada sublista es una modalidad completa, ocupaciones de menor a mayor.
        bloques = [
            ["90.00", "100.00"], ["85.50", "95.00"],
            ["96.90", "106.40"], ["102.00", "112.00"],
            ["90.00", "100.00"] * 2, ["85.50", "95.00"] * 2,
            ["96.90", "106.40", "108.30", "117.80"],
            ["102.00", "112.00", "114.00", "124.00"],
            ["120.00", "130.00"] * 2, ["114.00", "123.50"] * 2,
            ["125.40", "134.90", "136.80", "146.30"],
            ["132.00", "142.00", "144.00", "154.00"],
            ["140.00", "150.00"] * 4, ["133.00", "142.50"] * 4,
            ["144.40", "153.90", "155.80", "165.30", "167.20", "176.70", "178.60", "188.10"],
            ["152.00", "162.00", "164.00", "174.00", "176.00", "186.00", "188.00", "198.00"],
            ["115.00", "125.00"] * 3, ["109.25", "118.75"] * 3,
            ["120.65", "130.15", "132.05", "141.55", "143.45", "152.95"],
            ["127.00", "137.00", "139.00", "149.00", "151.00", "161.00"],
        ]
        self.assertEqual(controles.mock_calls, [evento for bloque in bloques for precio in bloque
                         for evento in (call.escribir(precio), call.pulsar_tab(), call.pausar(0.1))])

    def test_meses_completos(self):
        for mes, precios in configuracion.PRECIOS_2027.items():
            with self.subTest(mes=mes):
                filas = generar_circuito_completo(precios)
                self.assertEqual(len(filas), 48)
                self.assertTrue(all(len(f.tarifas) == len(precios) for f in filas))

    def test_mes_vacio_no_escribe(self):
        controles, esperar = Mock(), Mock()
        with patch.dict(configuracion.PRECIOS_2027, {"enero": []}, clear=True):
            ejecutar(controles=controles, leer=Mock(side_effect=["1", "1"]),
                     mostrar=Mock(), esperar=esperar)
        self.assertEqual(controles.mock_calls, [])
        esperar.assert_not_called()
