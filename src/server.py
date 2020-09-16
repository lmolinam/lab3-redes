import socket
import selectors
import time
import types
 

TIEMPO_ESPERA_CONEXIONES = 30
TIEMPO_ESPERA_RONDA = 15
MAX_CLIENTES = 7
MENSAJE_ESPERA = "Partida aún no empieza, por favor espere"


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

    conexiones = []
    while True:
        print("Esperando jugadores...")
        esperar_conexiones(selector, conexiones=conexiones)
        print(f"{len(conexiones)} jugadores listos, comienza el juego...")
        jugar_partida_blackjack(selector, conexiones)
        print("Partida finalizada, ¿Terminar de jugar? (ingresar q para finalizar)")
        message = input(" -> ")
        if message == "q":
            break

    print("Bajando Servidor...")
    for con in conexiones:
            con.close()
    my_socket.close()
    print("Servicio finalizado, hasta la próxima")


def esperar_conexiones(selector, conexiones=[], maximo_jugadores=MAX_CLIENTES, tiempo_espera=TIEMPO_ESPERA_CONEXIONES):
    tiempo_inicio = time.time()
    while len(conexiones) < maximo_jugadores:
        events = selector.select(timeout=tiempo_espera)
        for key, mask in events:
            if key.data == None:
                aceptar_conexion(key.fileobj, selector, selectors.EVENT_READ, conexiones)
            else:
                servir_cliente(key, mask, selector, conexiones, ready_to_play=False)

        if time.time() - tiempo_inicio >= tiempo_espera:
            print("Tiempo de espera completado")
            if(len(conexiones) == 0):
                print("Aún no hay jugadores conectados, se continua esperando")
            else:
                print(f"Hay {len(conexiones)} jugadores conectados, se deja de esperar")
                break
    
    return conexiones


def jugar_partida_blackjack(selector, conexiones=[], tiempo_espera=TIEMPO_ESPERA_RONDA):
    tiempo_inicio = time.time()
    while True:
        if time.time() - tiempo_inicio >= tiempo_espera:
            break

        events = selector.select(timeout=tiempo_espera)
        for key, mask in events:
            servir_cliente(key, mask, selector, conexiones)


def aceptar_conexion(sock, selector, events, conexiones):
    conn, addr = sock.accept()  # Should be ready to read
    print('Conexión aceptada desde', addr)
    conn.setblocking(False)
    #data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    data = types.SimpleNamespace(addr=addr)
    selector.register(conn, events, data)
    conexiones.append(conn)


def servir_cliente(key, mask, selector, conexiones, ready_to_play=True):
    conn = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = conn.recv(1024).decode()  # Should be ready to read
        if  recv_data and not ready_to_play:
            conn.send(MENSAJE_ESPERA.encode())
        elif recv_data:
            print(f"Data recibida desde {data.addr}: {recv_data}")
            respuesta = str(recv_data).upper()
            print (f"Enviando a {data.addr}:" + str(respuesta))
            conn.send(respuesta.encode())
        else:
            print('Cerrando conexión de', data.addr)
            selector.unregister(conn)
            conexiones.remove(conn)
            conn.close()


if __name__ == '__main__':
    main()


