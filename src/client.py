import socket
# import selectors

import blackjack 

def main():
        host = '127.0.0.1'
        port = 6060
        my_socket = socket.socket()
        my_socket.connect((host,port))

        print("Bienvenido a la mesa de blackjack online")

        message = ""
        jugador = blackjack.Jugador("local", 1)
         
        while message != 'q':
            my_socket.send("READY".encode())
            jugador.reset()
            print("Esperando el inicio de una nueva partida...")            
            mensaje_partida = recibir_mensaje(my_socket)

            recibir_primeras_cartas(my_socket, jugador)
            jugar(my_socket, jugador)
            
            resultado_final = recibir_mensaje(my_socket)
            print(resultado_final)

            print("Ingrese q para desconectarse, cualquier otro input para continuar...")
            message = input(" -> ")
                 
        my_socket.close()


def recibir_mensaje(socket):
    mensaje = socket.recv(1024).decode()
    if not mensaje:
        result = "Conexión terminada por parte de servidor"
        print(result)
        socket.close()
        raise ConnectionAbortedError(result)

    return mensaje


def recibir_primeras_cartas(socket, jugador):
    primeras_cartas = recibir_mensaje(socket)
    primera_carta, segunda_carta = blackjack.obtener_carta_desde_string(primeras_cartas)
    jugador.tomar_carta(primera_carta)
    jugador.tomar_carta(segunda_carta)


def jugar(socket, jugador):
    sigue_jugando = True
    while sigue_jugando:
        print(f"Mano actual:")
        for carta in jugador.obtener_mano():
            print(f"- Nombre: {carta.nombre}, Tipo: {carta.pinta}, Posibles valores: {carta.valores}")
        print(f"Mejor puntaje con mano actual: {jugador.obtener_maximo_puntaje_actual()}")
        print("Elija una opción:")
        print("1- Pedir otra carta")
        print("2- Plantarse con cartas actuales")
        opcion = input(" -> ") 
        opcion = opcion.strip()
        if opcion == blackjack.OPCION_PEDIR_CARTA:
            socket.send(blackjack.OPCION_PEDIR_CARTA.encode())
            nueva_carta = recibir_mensaje(socket)
            print(f"Carta recibida: {nueva_carta}")
            nueva_carta = blackjack.obtener_carta_desde_string(nueva_carta)
            try:
                jugador.tomar_carta(nueva_carta)
            except blackjack.ValorSobreBlackJack:
                print("Se ha sobrepasado el valor maximo de 21 con la nueva carta, no puede continuar jugando")
                print(f"Mano final:")
                for carta in jugador.obtener_mano():
                    print(f"- Nombre: {carta.nombre}, Tipo: {carta.pinta}, Posibles valores: {carta.valores}")                
                print(f"Puntaje final: {jugador.puntaje_final}")
                sigue_jugando = False
                socket.send(blackjack.OPCION_PERDIO.encode())
            except blackjack.ObtieneBlackJack:
                sigue_jugando = False
                print("¡Ha obtenido un BLACKJACK! (la suma de sus cartas da 21)")
                print(f"Mano final:")
                for carta in jugador.obtener_mano():
                    print(f"- Nombre: {carta.nombre}, Tipo: {carta.pinta}, Posibles valores: {carta.valores}")                
                print(f"Puntaje final: {jugador.puntaje_final}")
                socket.send(blackjack.OPCION_PLANTARSE.encode())
        elif opcion == blackjack.OPCION_PLANTARSE:
            try:
                jugador.plantarse()
            except blackjack.JugadorPlantado as jp:
                print(f"Se ha plantado con un puntaje total de {jugador.puntaje_final}")
                print(f"Esperando finalización de partida...")
                sigue_jugando = False
                socket.send(blackjack.OPCION_PLANTARSE.encode())
        else:
            print("Debe elegir una opción válida")

 
if __name__ == '__main__':
    main()