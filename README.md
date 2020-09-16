# lab3-redes

## Dependencias Relevantes
- Python 3.7+
- librería socket
- librería select (multiplexación)

## Descripción General

Servidor para hostear juegos de blackjack. Admite conexiones simultáneas de hasta 7 usuarios.

## Instrucciones de levantamiento

### Levantar Servidor

Para levantar el servidor es necesario ejecutar el archivo server.py ubicado en la carpeta src:

```bash 
▶ python3 server.py
Listening on ('127.0.0.1', 6060)
Esperando jugadores...
```

### Conectar Clientes

Luego de levantar el servidor podemos conectar clientes ejecutando el archivo client.py ubicado en la capreta src:

```bash
▶ python3 client.py
Bienvenido a la mesa de blackjack online
Esperando el inicio de una nueva partida...
```

## Manual de uso

A continuación se muestra en mayor detalle el uso y ciclo de vida del servidor blackjack y sus clientes

### Servidor

#### Espera de conexiones

Una vez inicializado el servidor se esperara un tiempo inicial por jugadores, luego si aún no hay jugadores conectados esperará indefinidamente por conexiones de jugadores antes de empezar una partida. Se necesita que al menos un jugador se conecte para comenzar.

```bash 
▶ python3 server.py
Listening on ('127.0.0.1', 6060)
Esperando jugadores...
Tiempo de espera completado
Aún no hay jugadores conectados, se continua esperando
```

#### Acciones de Croupier
Una vez comenzada la partida el croupier (quien reparte cartas y juega representando a la casa) revisa sus cartas. El croupier apunta a tener un minimo de 17, si acanza o excede este mínimo se detiene.

```bash
Tiempo de espera completado
Hay 4 jugadores conectados, se deja de esperar
4 jugadores listos, comienza el juego...
crouper maximo puntaje acutal 17
* Croupier finalizó de jugar con un puntaje de 17 *
Mano actual Croupier:
- Nombre: SIX, Tipo: DIAMANTE, Posibles valores: [6]
- Nombre: AS, Tipo: DIAMANTE, Posibles valores: [1, 11]
```

#### Espera de confirmación por parte de jugadores

Luego de que todos los jugadores jueguen sus cartas la partida finalizara y el servidor anunciara los resultados a si mismo y a todos sus clientes, pasando a una espera en que todos los jugadores deben confirmar si seguirán participando o se desconectarán. Adicionalmente el servidor va mostrando en tiempo real que jugadores ya han perdido y cuales ya se "plantaron" con su puntaje.

```bash
* Jugador 1 ha PERDIDO con un puntaje total de 26 *
* Jugador 2 ha PERDIDO con un puntaje total de 23 *
* Jugador 3 ha PERDIDO con un puntaje total de 25 *
* Jugador 4 se ha PLANTADO con un puntaje total de 18 *
* !Partida Terminada! *
* El ganador es Jugador 4 con un puntaje de 18 *
Esperando cierres/confirmaciones de jugadores...
```

#### Continuación/Finalización de Servidor

El servidor va mostrando en tiempo real quienes se desconectan y quienes confirman que seguirán jugando. Una vez todos los jugadores hayan respondido se da la opción de iniciar una nueva partida de blackjack (repitiendo los pasos anteriores) o en su defecto detener la ejecución del servidor ingresando la letra "q".

```bash
Esperando cierres/confirmaciones de jugadores...
Cerrando conexión de ('127.0.0.1', 36324)
Cerrando conexión de ('127.0.0.1', 36326)
Paquete recibido desde Jugador 1, se omite ya que aún no comienza partida
Paquete recibido desde Jugador 2, se omite ya que aún no comienza partida
Partida finalizada, ¿Terminar de jugar? (ingresar q para finalizar)
```


### Clientes

#### Espera de Inicio de partida

Los clientes solo pueden conectarse en durante el tiempo de espera previo a una partida. Estos al conectarse deben esperar el tiempo minimo configurado en el servidor para esta etapa (20 segundos)

```bash
▶ python3 client.py
Bienvenido a la mesa de blackjack online
Esperando el inicio de una nueva partida...
```

#### Acciones de Jugadores

Al iniciar la partida a cada jugador se le entregaran 2 cartas. El jugador puede solicitar cartas hasta que se pase (o llegue) al máximo que es 21. Adicionalmente el jugador se puede "plantar" es decir detenerse con las cartes y el puntaje que tiene a la espera de que los demás jugadores terminen.

Ejemplo 1:
```bash
Bienvenido a la mesa de blackjack online
Esperando el inicio de una nueva partida...
Mano actual:
- Nombre: JACK, Tipo: TREBOL, Posibles valores: [10]
- Nombre: THREE, Tipo: CORAZON, Posibles valores: [3]
Mejor puntaje con mano actual: 13
Elija una opción:
1- Pedir otra carta
2- Plantarse con cartas actuales
 -> 
```

Ejemplo 2:
```bash
Mejor puntaje con mano actual: 15
Elija una opción:
1- Pedir otra carta
2- Plantarse con cartas actuales
 -> 1
Carta recibida: TEN | PICA
Se ha sobrepasado el valor maximo de 21 con la nueva carta, no puede continuar jugando
Mano final:
- Nombre: SEVEN, Tipo: DIAMANTE, Posibles valores: [7]
- Nombre: EIGTH, Tipo: CORAZON, Posibles valores: [8]
- Nombre: TEN, Tipo: PICA, Posibles valores: [10]
Puntaje final: 25
* !Partida Terminada! *
* El ganador es Jugador 4 con un puntaje de 18 *
Ingrese q para desconectarse, cualquier otro input para continuar...
 ->
```

#### Continuación/Finalización de Jugadores

Una vez todos los jugadores terminen de realizar sus acciones la partida finaliza y los ganadores son anunciados a todos los participantes. Luego cada jugador puede decidir si se desconecta del servidor ingresando la letra "q" o si continua para la próxima partida ingresando cualquier otro input para continuar.

```bash
* !Partida Terminada! *
* El ganador es Jugador 2 con un puntaje de 21 *
Ingrese q para desconectarse, cualquier otro input para continuar...
 -> on
Esperando el inicio de una nueva partida...

Se ha plantado con un puntaje total de 18
Esperando finalización de partida...
* !Partida Terminada! *
* El ganador es Jugador 2 con un puntaje de 21 *
Ingrese q para desconectarse, cualquier otro input para continuar...
 -> q
```

### Configuraciones

En el archivo server.py podemos encontrar las siguientes variables relevantes:

TIEMPO_ESPERA_CONEXIONES = 20 -> indica el tiempo de espera minimo en la fase de espera de jugadores
MAX_CLIENTES = 7 -> indica el número máximo de jugadores esperados para una partida



