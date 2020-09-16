import socket
import selectors
import time
import types

import blackjack


TIEMPO_ESPERA_CONEXIONES = 5
TIEMPO_ESPERA_RONDA = 15
MAX_CLIENTES = 7
MENSAJE_ESPERA = "Partida aun no empieza, por favor espere"
MENSAJE_RECHAZO = "Partida en progreso, no se admiten conexiones"
MENSAJE_INCIO_PARTIDA = "¡La partida ha comenzado!"
MENSAJE_FIN_PARTIDA = "!La partida ha terminado!"
MESA_BLACKJACK = blackjack.MesaBlackJack(1)

def main():
    host = "127.0.0.1"
    port = 6060
    my_socket = socket.socket()
    my_socket.bind((host,port))
    my_socket.listen(MAX_CLIENTES)
    my_socket.setblocking(False)
    selector = selectors.DefaultSelector()
    selector.register(my_socket, selectors.EVENT_READ, data=None)
    print('Listening on', (host, port))

    conn_jugadores = []
    message = ""
    while message != "q":
        print("Esperando jugadores...")
        esperar_conexiones(selector, conn_jugadores=conn_jugadores)
        print(f"{len(conn_jugadores)} jugadores listos, comienza el juego...")
        notificar_comienzo_partida(conn_jugadores)
        mensaje_fin = jugar_partida_blackjack(selector, conn_jugadores)
        print(mensaje_fin)
        notificar_fin_partida(conn_jugadores, mensaje_fin)
        print("Esperando cierres/confirmaciones de jugadores...")
        esperar_cierres(selector, len(MESA_BLACKJACK.jugadores), conn_jugadores)
        print("Partida finalizada, ¿Terminar de jugar? (ingresar q para finalizar)")
        message = input(" -> ")

    print("Bajando Servidor...")
    for conn_jugador in conn_jugadores:
            conn_jugador.conn.close()
    my_socket.close()
    print("Servicio finalizado, hasta la próxima")


def esperar_conexiones(selector, conn_jugadores=[], maximo_jugadores=MAX_CLIENTES, tiempo_espera=TIEMPO_ESPERA_CONEXIONES):
    tiempo_inicio = time.time()
    while len(conn_jugadores) < maximo_jugadores:
        events = selector.select(timeout=tiempo_espera)
        for key, mask in events:
            if key.data == None:
                aceptar_conexion(key.fileobj, selector, selectors.EVENT_READ, conn_jugadores)
            else:
                servir_cliente(key, mask, selector, conn_jugadores, ready_to_play=False)

        if time.time() - tiempo_inicio >= tiempo_espera:
            print("Tiempo de espera completado")
            if(len(conn_jugadores) == 0):
                print("Aún no hay jugadores conectados, se continua esperando")
            else:
                print(f"Hay {len(conn_jugadores)} jugadores conectados, se deja de esperar")
                break
    
    return conn_jugadores

def notificar_comienzo_partida(conn_jugadores):
    for conn_jugador in conn_jugadores: 
        conn_jugador.conn.send(MENSAJE_INCIO_PARTIDA.encode())

def notificar_fin_partida(conn_jugadores, mensaje_fin):
    for conn_jugador in conn_jugadores: 
        conn_jugador.conn.send(mensaje_fin.encode())

def _iniciar_ronda(conn_jugadores):
    MESA_BLACKJACK.nueva_ronda()
    MESA_BLACKJACK.ronda_actual.dar_mano_inicial()
    for conn_jugador in conn_jugadores: 
        jugador = blackjack.obtener_jugador(conn_jugador.numero_jugador, jugadores=MESA_BLACKJACK.jugadores)
        cartas_iniciales = jugador.obtener_mano()
        conn_jugador.conn.send(f"{cartas_iniciales[0].nombre} | {cartas_iniciales[0].pinta} & {cartas_iniciales[1].nombre} | {cartas_iniciales[1].pinta}".encode())

def jugar_partida_blackjack(selector, conn_jugadores=[], tiempo_espera=TIEMPO_ESPERA_RONDA):
    tiempo_inicio = time.time()
    _iniciar_ronda(conn_jugadores)
    croupier = MESA_BLACKJACK.croupier
    jugar_croupier = True
    print(f"crouper maximo puntaje acutal {croupier.obtener_maximo_puntaje_actual()}")
    print(f"* Croupier finalizó de jugar con un puntaje de {croupier.puntaje_final} *")
    print(f"Mano actual Croupier:")
    for carta in croupier.obtener_mano():
        print(f"- Nombre: {carta.nombre}, Tipo: {carta.pinta}, Posibles valores: {carta.valores}")

    while True:
        # if (time.time() - tiempo_inicio >= tiempo_espera) or MESA_BLACKJACK.ronda_actual.jugadores_pendientes == 0:
        #     break
        if jugar_croupier:
            try:
                MESA_BLACKJACK.ronda_actual.dar_carta(MESA_BLACKJACK.croupier.numero)
            except blackjack.JugadorPlantado:
                jugar_croupier = False
            else:
                print(f"Mano final croupier:")
                for carta in croupier.obtener_mano():
                    print(f"- Nombre: {carta.nombre}, Tipo: {carta.pinta}, Posibles valores: {carta.valores}")
        
        if len(MESA_BLACKJACK.ronda_actual.jugadores_pendientes) == 0:
            mensaje_final = MESA_BLACKJACK.terminar_ronda()
            return mensaje_final

        events = selector.select(timeout=tiempo_espera)
        for key, mask in events:
            if key.data == None:
                rechazar_conexion(key.fileobj)
            else:
                servir_cliente(key, mask, selector, conn_jugadores)


def esperar_cierres(selector, cantidad_jugadores, conn_jugadores,tiempo_espera=TIEMPO_ESPERA_CONEXIONES):
    cierres = 0
    while cierres < cantidad_jugadores - 1:
        events = selector.select(timeout=tiempo_espera)
        for key, mask in events:
            if key.data == None:
                rechazar_conexion(key.fileobj)
            else:
                servir_cliente(key, mask, selector, conn_jugadores, ready_to_play=False)
                cierres += 1
    
    return cierres

def aceptar_conexion(sock, selector, events, conn_jugadores):
    conn, addr = sock.accept()  # Should be ready to read
    print('Conexión aceptada desde', addr)
    conn.setblocking(False)

    numero_jugador = len(conn_jugadores) + 1
    jugador = blackjack.Jugador(f"Jugador {numero_jugador}", numero_jugador)
    MESA_BLACKJACK.agregar_jugador(jugador)
    conn_jugador = types.SimpleNamespace(conn=conn, numero_jugador=numero_jugador)
    conn_jugadores.append(conn_jugador)
    
    data = types.SimpleNamespace(addr=addr, conn_jugador=conn_jugador)
    selector.register(conn_jugador.conn, events, data)

def rechazar_conexion(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('Conexión rechazada desde, Hay una partida en progreso', addr)
    conn.send(MENSAJE_RECHAZO.encode())
    conn.close()

def servir_cliente(key, mask, selector, conn_jugadores, ready_to_play=True):
    conn = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = conn.recv(1024).decode()  # Should be ready to read
        jugador = blackjack.obtener_jugador(data.conn_jugador.numero_jugador, jugadores=MESA_BLACKJACK.jugadores)
        if  recv_data and not ready_to_play:
            print(f"Se omite comunicación con {jugador.nombre} ya que aún no comienza partida")
        elif recv_data:
            if recv_data == blackjack.OPCION_PEDIR_CARTA:
                try:
                    MESA_BLACKJACK.ronda_actual.dar_carta(data.conn_jugador.numero_jugador)
                except blackjack.JugadorPlantado:
                    respuesta = "Jugador ya no se encuentra activo para esta ronda, esta en espera de resultados"
                except blackjack.CartasAgotadas:
                    respuesta = "Cartas agotadas, se termina ronda."
                else:
                    respuesta = f"{jugador.ultima_carta.nombre} | {jugador.ultima_carta.pinta}"
                    conn.send(respuesta.encode())
            elif recv_data == blackjack.OPCION_PLANTARSE:
                try:
                    MESA_BLACKJACK.ronda_actual.plantar_jugador(data.conn_jugador.numero_jugador)
                except blackjack.JugadorPlantado as jp:
                    print(f"* Jugador {data.conn_jugador.numero_jugador} se ha PLANTADO con un puntaje total de {jugador.puntaje_final} *")
            elif recv_data == blackjack.OPCION_PERDIO:
                print(f"* Jugador {data.conn_jugador.numero_jugador} ha PERDIDO con un puntaje total de {jugador.puntaje_final} *")
        else:
            print('Cerrando conexión de', data.addr)
            selector.unregister(data.conn_jugador.conn)
            conn_jugadores.remove(data.conn_jugador)
            data.conn_jugador.conn.close()
            MESA_BLACKJACK.remover_jugador(data.conn_jugador.numero_jugador)


if __name__ == '__main__':
    main()


