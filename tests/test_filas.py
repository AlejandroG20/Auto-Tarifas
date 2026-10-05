import unittest
from decimal import Decimal
from unittest.mock import Mock, call, patch

from tarifas import configuracion
from tarifas.calculo import calcular_precio, generar_tarifas_filas, obtener_precios_mes
from tarifas.configuracion import CampoTarifa
from tarifas.consola import ejecutar
from tarifas.entrada import seleccionar_mes, seleccionar_tarifa


class FilasTests(unittest.TestCase):
    def test_ocupaciones_y_suplementos(self):
        esperadas = {"INDIVIDUAL": ([1], 0), "DOBLE_EXECUTIVE": ([1, 2], 0),
                     "PREMIUM": ([1, 2], 30), "TRIPLE": ([1, 2, 3], 25),
                     "SUITE": ([1, 2, 3, 4], 50)}
        for tipo, (ocupaciones, suplemento) in esperadas.items():
            for desayuno in (False, True):
                for nr in (False, True):
                    with self.subTest(tipo=tipo, desayuno=desayuno, nr=nr):
                        filas = generar_tarifas_filas(CampoTarifa(tipo, desayuno=desayuno,
                                                                 no_reembolsable=nr), [90, 100])
                        self.assertEqual([f.personas for f in filas], ocupaciones)
                        for fila in filas:
                            esperado = tuple((Decimal(base + suplemento +
                                (12 * fila.personas if desayuno else 0)) *
                                (Decimal("0.95") if nr else Decimal(1))).quantize(
                                    Decimal("0.01")) for base in (90, 100))
                            self.assertEqual(fila.tarifas, esperado)
                            self.assertTrue(all(isinstance(v, Decimal) and v.as_tuple().exponent == -2
                                                for v in fila.tarifas))

    def test_individual_equivale_exe(self):
        self.assertEqual(calcular_precio(90, "INDIVIDUAL", 1, True, True),
                         calcular_precio(90, "EXE", 1, True, True))
        self.assertEqual(generar_tarifas_filas(CampoTarifa("EXE"), [90]),
                         generar_tarifas_filas(CampoTarifa("INDIVIDUAL"), [90]))

    def test_redondeo_filas_al_final(self):
        filas = generar_tarifas_filas(CampoTarifa("DOBLE_EXECUTIVE", desayuno=True,
                                      no_reembolsable=True), [Decimal("90.10")])
        self.assertEqual([f.tarifas for f in filas], [(Decimal("97.00"),), (Decimal("108.40"),)])

    def test_menu_mes_y_validacion(self):
        leer = Mock(side_effect=["0", "abc", "13", "2"])
        self.assertEqual(seleccionar_mes(leer, Mock()), "febrero")
        for mes, precios in configuracion.PRECIOS_2027.items():
            self.assertEqual(obtener_precios_mes(mes), tuple(precios))
        for mes in ("otro", None, []):
            with self.assertRaises(ValueError):
                obtener_precios_mes(mes)
        with patch.dict(configuracion.PRECIOS_2027, {}, clear=True):
            with self.assertRaises(ValueError):
                seleccionar_mes(Mock(), Mock())

    def test_menu_no_pide_huespedes(self):
        for desayuno in ("1", "2"):
            leer = Mock(side_effect=["5", desayuno, "2"])
            seleccion = seleccionar_tarifa(leer, Mock())
            self.assertEqual(seleccion.tipo_habitacion, "SUITE")
            self.assertEqual(leer.call_count, 3)

    def test_precio_ausente_no_escribe(self):
        controles, esperar = Mock(), Mock()
        with patch.dict(configuracion.PRECIOS_2027, {"junio": [90, None]}, clear=True):
            with self.assertRaises(ValueError):
                ejecutar(controles=controles, leer=Mock(side_effect=["1", "1"]),
                         mostrar=Mock(), esperar=esperar)
        controles.assert_not_called()
        self.assertEqual(controles.mock_calls, [])
        esperar.assert_not_called()
