# Auto-Tarifas

Base modular para Python 3.10 o posterior. No ejecuta pulsaciones al importar módulos.

- `tarifas/configuracion.py`: suplementos, desayuno, `PRECIOS_EXE`, orden de campos y pausas.
- `tarifas/calculo.py`: cálculo independiente de PyAutoGUI, con importes `Decimal` sin redondeo implícito.
- `tarifas/automatizacion.py`: adaptador de teclado, escritura y coordinación de días.

Introducir los precios diarios EXE sin desayuno en `PRECIOS_EXE`, respetando su orden.
`calcular_precio(90, "TRIPLE", personas=3, desayuno=True)` devuelve `Decimal('151')`.
Sin desayuno, la ocupación no cambia el importe. Se rechazan precios no positivos,
valores no finitos, tipos desconocidos y ocupaciones negativas o no enteras.

## Configuración pendiente

`ORDEN_TARIFAS` permanece vacío hasta conocer las casillas reales. Cada entrada será
un `CampoTarifa(tipo_habitacion, personas=0, desayuno=False)`. Se respetan exactamente
el orden y las repeticiones de esas entradas. No se deduce ningún orden del diccionario
de suplementos. Preparar o procesar días con el orden vacío produce un error explícito.

`preparar_dias()` calcula y valida todos los días sin interacción con el programa externo.
`procesar_dias()` exige `cambiar_dia(numero)` para procesar más de un día; esa función
deberá navegar y enfocar la primera casilla del día indicado. Su implementación está
pendiente de conocer el programa externo. No se simula la navegación con TAB adicionales.

## Integración

Instalar `pip install -r requirements.txt` para la automatización. El cálculo y las
pruebas no necesitan PyAutoGUI. La interfaz deberá enfocar la primera casilla antes
de llamar a `escribir_tarifas(tarifas)` o `procesar_dias(...)`.
La escritura emite `precio → TAB` para cada importe, incluido el último, y hace la pausa
configurada. No selecciona ni borra contenido previamente: debe confirmarse cómo se
editan las casillas del programa. El separador decimal es configurable mediante
`separador_decimal="."` o `","`; no se redondean los importes.

Se puede inyectar `controles` con métodos `escribir`, `pulsar_tab` y `pausar` para
integrar auxiliares de una interfaz o probar sin teclado. Los errores se propagan;
si falla la automatización tras escribir, no se reintenta ni se reanuda automáticamente.
El adaptador conserva el mecanismo de emergencia predeterminado de PyAutoGUI.

La aplicación que integre estos módulos puede activar los logs con
`logging.basicConfig(level=logging.INFO, format="%(message)s")`. Se registra una línea
por día; las tarifas individuales solo aparecen en nivel DEBUG.

Pruebas: `python -m unittest discover -s tests -v`.
