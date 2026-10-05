import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

from tarifas import configuracion
from tarifas.calculo import generar_circuito_mirai, obtener_precios_bimestre
from tarifas.consola import ejecutar
from tarifas.entrada import seleccionar_flujo, seleccionar_bimestre


class MiraiTests(unittest.TestCase):
    def test_orden_y_calculos_capturas(self):
        filas = generar_circuito_mirai(iter([81, 79]))
        habitaciones = [
            ("EXE", [(2, 0), (1, 0), (1, 1)], 0),
            ("PREMIUM", [(2, 0), (1, 0), (1, 1)], 30),
            ("TRIPLE", [(2, 1), (3, 0)], 25),
            ("SUITE", [(2, 0), (2, 1), (4, 0), (3, 0), (3, 1), (1, 0), (1, 1)], 50),
        ]
        esperado = [(tipo, ocupacion, ad, nr, suplemento)
                    for tipo, ocupaciones, suplemento in habitaciones
                    for nr in (False, True) for ocupacion in ocupaciones
                    for ad in (False, True)]
        self.assertEqual(len(filas), 60)
        for fila, (tipo, ocupacion, ad, nr, suplemento) in zip(filas, esperado):
            self.assertEqual((fila.seleccion.tipo_habitacion, fila.ocupacion,
                              fila.seleccion.desayuno, fila.seleccion.no_reembolsable),
                             (tipo, ocupacion, ad, nr))
            valores = tuple(
                (Decimal(base + suplemento + (12 * sum(ocupacion) if ad else 0))
                 * (Decimal("0.95") if nr else Decimal(1))).quantize(Decimal("0.01"))
                for base in (81, 79))
            self.assertEqual(fila.tarifas, valores)
        self.assertEqual(filas[7].tarifas[0], Decimal("99.75"))
        self.assertEqual(filas[45].tarifas[0], Decimal("155.00"))
        self.assertEqual(filas[47].tarifas[0], Decimal("147.25"))

    def test_bimestres_y_frontera(self):
        for pareja in configuracion.BIMESTRES_MIRAI:
            self.assertEqual(obtener_precios_bimestre(pareja),
                             tuple(configuracion.PRECIOS_2027[pareja[0]]
                                   + configuracion.PRECIOS_2027[pareja[1]]))
        with patch.dict(configuracion.PRECIOS_2027,
                        {"enero": [81] * 31, "febrero": [79] * 28}):
            precios = obtener_precios_bimestre(("enero", "febrero"))
            self.assertEqual(precios[30:32], (81, 79))

    def test_menu_reintenta(self):
        leer = Mock(side_effect=["0", "Mirai", "2", "7", "6"])
        self.assertEqual(seleccionar_flujo(leer, Mock()), "Mirai")
        self.assertEqual(seleccionar_bimestre(leer, Mock()), ("noviembre", "diciembre"))

    def test_consola_mirai(self):
        controles, leer, mostrar = Mock(), Mock(side_effect=["2", "1", "1"]), Mock()
        with patch.dict(configuracion.PRECIOS_2027,
                        {"enero": [81] * 31, "febrero": [79] * 28}):
            ejecutar(controles=controles, leer=leer, mostrar=mostrar, esperar=Mock())
        self.assertEqual(leer.call_count, 3)
        valores = [c.args[0] for c in controles.escribir.call_args_list]
        self.assertEqual(len(valores), 708)
        self.assertEqual(valores[:32], ["81,00"] * 31 + ["79,00"])
        self.assertEqual(valores[59:91], ["105,00"] * 31 + ["103,00"])
        self.assertEqual(controles.pulsar_tab.call_count, 708)
        self.assertTrue(any("ocupacion 2 + 0" in c.args[0] for c in mostrar.call_args_list))

    def test_mes_incompleto_o_precio_invalido_no_escribe(self):
        for valores in ([81], [81] * 30 + [None]):
            controles, esperar = Mock(), Mock()
            with patch.dict(configuracion.PRECIOS_2027, {"enero": valores}):
                with self.assertRaises(ValueError):
                    ejecutar(controles=controles, leer=Mock(side_effect=["2", "1"]),
                             mostrar=Mock(), esperar=esperar)
            self.assertEqual(controles.mock_calls, [])
            esperar.assert_not_called()

    def test_escritura_separada_por_habitacion(self):
        for opcion, tipo, filas, primera, ocupacion in [
            ("1", "EXE", 12, "81,00", "2 + 0"),
            ("2", "PREMIUM", 12, "111,00", "2 + 0"),
            ("3", "TRIPLE", 8, "106,00", "2 + 1"),
            ("4", "SUITE", 28, "131,00", "2 + 0"),
        ]:
            with self.subTest(habitacion=tipo):
                controles, mostrar = Mock(), Mock()
                ejecutar([81, 79], controles=controles,
                         leer=Mock(side_effect=["2", "1", opcion]),
                         mostrar=mostrar, esperar=Mock())
                esperado = [v for f in generar_circuito_mirai([81, 79])
                            if f.seleccion.tipo_habitacion == tipo for v in f.tarifas]
                valores = [c.args[0] for c in controles.escribir.call_args_list]
                self.assertEqual(valores, [format(v, ".2f").replace(".", ",")
                                          for v in esperado])
                self.assertEqual(len(valores), filas * 2)
                self.assertEqual(valores[0], primera)
                self.assertTrue(any(f"dia 1 de {tipo}, BAR" in c.args[0]
                                    and f"ocupacion {ocupacion}" in c.args[0]
                                    for c in mostrar.call_args_list))
