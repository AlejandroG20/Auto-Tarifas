# Auto-Tarifas

Base modular para Python 3.10 o posterior. No ejecuta pulsaciones al importar módulos.

## Uso por consola

Instalar `pip install -r requirements.txt` y ejecutar `python -m tarifas`.

Al arrancar, elegir primero **1. FNS** o **2. Mirai**.

En FNS, seleccionar el mes de `PRECIOS_2027`. El programa prepara el circuito
completo de Individual, Doble Executive, Premium, Suite y Triple, en ese orden.
En cada habitacion escribe los cuatro bloques mostrados por el programa externo:

1. Tarifa estandar (sin desayuno).
2. Oferta no reembolsable (sin desayuno, -5 %).
3. No reembolsable HD (con desayuno, -5 % sobre el total).
4. Alojamiento con desayuno incluido (estandar).

Dentro de cada bloque completa todos los dias de 1 Pax, despues 2 Pax, etc.
Ocupaciones: Individual 1; Doble y Premium 1-2; Suite 1-4; Triple 1-3.
Son 48 filas: 1.440 precios en un mes de 30 dias.
Se mantienen los suplementos y el desayuno de 12 euros por huesped.

Tras el resumen hay 5 segundos para enfocar el dia 1 de Individual, tarifa
estandar, 1 Pax. La escritura continua mediante `PRECIO -> TAB`, incluido el
ultimo TAB, sin agregar navegacion ni pulsar Guardar. El mes mostrado en el
programa externo debe coincidir con el seleccionado. Al terminar, revisar y guardar
los cambios en el programa externo. Ctrl+C cancela en la consola.

`ORDEN_HABITACIONES` y `MODALIDADES` definen el orden del circuito;
`generar_circuito_completo` calcula y valida sus filas antes de escribir.
Las API de seleccion y calculo de una sola tarifa se conservan para integraciones.

Los precios base se mantienen en `PRECIOS_2027`; ya no hay que cambiar `PRECIOS_EXE`
para elegir mes. Un mes vacio no escribe. Los valores pendientes `None` se rechazan
antes de cualquier pulsacion; completar esos precios antes de utilizar ese mes.

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

- `tarifas/configuracion.py`: ocupaciones, suplementos, desayuno, `PRECIOS_2027`, orden de campos y pausas.
- `tarifas/calculo.py`: cálculo independiente de PyAutoGUI, con importes `Decimal` sin redondeo implícito.
- `tarifas/automatizacion.py`: adaptador de teclado, escritura y coordinación de días.
- `tarifas/entrada.py`: menús con reintentos ante entradas inválidas.
- `tarifas/formato.py`: representación monetaria y separador decimal.
- `tarifas/registros.py`: resumen y logs diarios.
- `tarifas/consola.py`: coordinación; `__main__.py`: punto de entrada.

Introducir los precios diarios EXE sin desayuno en cada mes de `PRECIOS_2027`, respetando su orden.
`PRECIOS_EXE` y las API anteriores se conservan para integraciones existentes.
`generar_tarifas_filas` devuelve las filas de ocupacion y sus importes diarios.
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


## Mirai

Cada ejecucion procesa una sola habitacion. Elegir el bimestre y despues
1. EXE, 2. Premium, 3. Triple o 4. Suite. Al terminar se detiene; volver a
ejecutar el programa para la siguiente habitacion.

Elegir un bimestre de 2027: enero-febrero, marzo-abril, mayo-junio,
julio-agosto, septiembre-octubre o noviembre-diciembre. Los precios proceden
de los mismos meses de `PRECIOS_2027`; se concatenan los dias de ambos meses.
Se exige que ambos meses tengan todos sus precios antes de escribir.

Orden: EXE, Premium, Triple y Suite. En cada habitacion se completa BAR y
despues NRF (-5 %). Para cada ocupacion se escribe Solo Alojamiento y despues
Desayuno Incluido, recorriendo todos los dias del bimestre en cada fila.

- EXE y Premium: 2 + 0, 1 + 0, 1 + 1.
- Triple: 2 + 1, 3 + 0.
- Suite: 2 + 0, 2 + 1, 4 + 0, 3 + 0, 3 + 1, 1 + 0, 1 + 1.

El desayuno cuenta adultos y menores a 12 euros por persona; NRF descuenta
el total con desayuno. Son 12 filas para EXE, 12 para Premium, 8 para Triple y 28 para Suite. Mirai utiliza coma decimal, configurable
con `SEPARADOR_DECIMAL_MIRAI`. Los ceros de las capturas son valores existentes,
no precios base nuevos: el programa calcula los importes desde `PRECIOS_2027`.

Enfocar el dia 1 de la habitacion elegida, BAR, Solo Alojamiento: ocupacion
2 + 1 para Triple y 2 + 0 para EXE, Premium o Suite.
El bimestre visible en Mirai debe coincidir con el elegido y las habitaciones
deben estar desplegadas. Se conserva la escritura precio -> TAB; revisar
y guardar manualmente al terminar. La navegacion real de Mirai requiere
comprobar que TAB recorre esas casillas en el orden mostrado.


## Pausar la escritura

En Windows, pulsar **F8** durante la escritura para pausarla y volver a pulsar
**F8** para continuar. Funciona con FNS o Mirai enfocado. Se completa el precio
y TAB en curso antes de pausar; se reanuda desde la siguiente casilla pendiente.
Mantener el foco en esa casilla antes de reanudar. Ctrl+C en la consola cancela
tambien durante la pausa. El atajo solo esta activo durante la escritura real
y se libera al finalizar o cancelar.
