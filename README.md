# Auto-Tarifas

Base modular para Python 3.10 o posterior. No ejecuta pulsaciones al importar módulos.

## Uso por consola

Instalar `pip install -r requirements.txt`. Editar `tarifas/configuracion.py`, por ejemplo:

```python
PRECIOS_EXE = [Decimal("90"), Decimal("100"), Decimal("110")]
```

Los precios base son EXE sin desayuno y reembolsables. Ejecutar desde esta carpeta:

```text
python -m tarifas
```

Seleccionar habitación, desayuno, huéspedes (solo con desayuno) y modalidad.
Se muestra el resumen y todos los precios; después hay 5 segundos para enfocar la
primera casilla del programa externo. Esta espera se configura en `SEGUNDOS_PARA_ENFOCAR`.
Ctrl+C cancela mientras la consola tenga el foco.
Con el array vacío se informa de que faltan precios y no se ejecutan pulsaciones.

PREMIUM con desayuno para 2 huéspedes y no reembolsable genera:
`136.80 → TAB → 146.30 → TAB → 155.80 → TAB`.
Este flujo de una única combinación usa directamente `escribir_tarifas`, sin necesitar
`ORDEN_TARIFAS` ni añadir navegación. Los campos diarios deben estar dispuestos en
la secuencia de TAB solicitada.

El descuento central `DESCUENTO_NO_REEMBOLSABLE = Decimal("0.05")` se aplica al total,
incluido el desayuno. Se calcula con `Decimal` y solo al final se redondea a céntimos
con `ROUND_HALF_UP`. Usar enteros o `Decimal("90.50")` en la configuración; las entradas
numéricas heredadas se convierten a `Decimal`. La conversión a float del adaptador
se limita al tiempo de espera, nunca a cálculos monetarios.

```python
from tarifas.calculo import calcular_precio, generar_tarifas_diarias
from tarifas.configuracion import CampoTarifa

precio = calcular_precio(90, "PREMIUM", desayuno=True, huespedes=2,
                        no_reembolsable=True)
tarifas = generar_tarifas_diarias(CampoTarifa("PREMIUM", 2, True, True))
```

Se mantiene la firma posicional `(precio_exe, tipo_habitacion, personas, desayuno)`.
`huespedes` es un alias por nombre: utilizar solo uno de los nombres de ocupación.
Con desayuno se exige un entero de al menos 1; sin desayuno se ignora una ocupación
válida. Nunca se admiten ocupaciones negativas. La modalidad debe ser un booleano.

## Estructura

- `tarifas/configuracion.py`: suplementos, desayuno, `PRECIOS_EXE`, orden de campos y pausas.
- `tarifas/calculo.py`: cálculo independiente de PyAutoGUI, con importes `Decimal` sin redondeo implícito.
- `tarifas/automatizacion.py`: adaptador de teclado, escritura y coordinación de días.
- `tarifas/entrada.py`: menús con reintentos ante entradas inválidas.
- `tarifas/formato.py`: representación monetaria y separador decimal.
- `tarifas/registros.py`: resumen y logs diarios.
- `tarifas/consola.py`: coordinación; `__main__.py`: punto de entrada.

Introducir los precios diarios EXE sin desayuno en `PRECIOS_EXE`, respetando su orden.
`calcular_precio(90, "TRIPLE", personas=3, desayuno=True)` devuelve `Decimal('151.00')`.
Sin desayuno, la ocupación no cambia el importe. Se rechazan precios no positivos,
valores no finitos, tipos desconocidos y ocupaciones negativas o no enteras.

## Flujo anterior de múltiples campos por día: configuración pendiente

`ORDEN_TARIFAS` permanece vacío hasta conocer las casillas reales. Cada entrada será
un `CampoTarifa(tipo_habitacion, personas=0, desayuno=False, no_reembolsable=False)`. Se respetan exactamente
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
`SEPARADOR_DECIMAL` en configuración o el argumento `separador_decimal="."` o `","`.
La escritura siempre utiliza dos decimales con el redondeo monetario configurado.

Se puede inyectar `controles` con métodos `escribir`, `pulsar_tab` y `pausar` para
integrar auxiliares de una interfaz o probar sin teclado. Los errores se propagan;
si falla la automatización tras escribir, no se reintenta ni se reanuda automáticamente.
El adaptador conserva el mecanismo de emergencia predeterminado de PyAutoGUI.

La aplicación que integre estos módulos puede activar los logs con
`logging.basicConfig(level=logging.INFO, format="%(message)s")`. Se registra una línea
por día en el flujo anterior; sus tarifas individuales solo aparecen en nivel DEBUG.
La consola activa INFO y muestra la configuración, el número de días y cada precio final.

Pruebas: `python -m unittest discover -s tests -v`.
