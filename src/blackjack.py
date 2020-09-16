import random

BLACK_JACK = 21
OPCION_PEDIR_CARTA = "1"
OPCION_PLANTARSE = "2"
OPCION_PERDIO = "3"
TOKEN_SEPARACION_DATOS_CARTA = "|"
TOKEN_SEPARACION_CARTAS = "&"
TREBOL = "TREBOL"
PICA = "PICA"
DIAMANTE = "DIAMANTE"
CORAZON = "CORAZON"
PINTAS = [TREBOL, PICA, DIAMANTE, CORAZON]
AS = "AS"
TWO = "TWO"
THREE = "THREE"
FOUR = "FOUR"
FIVE = "FIVE"
SIX = "SIX"
SEVEN = "SEVEN"
EIGTH = "EIGTH"
NINE = "NINE"
TEN = "TEN"
JACK = "JACK"
QUEEN = "QUEEN"
KING = "KING"
NUMERICAS = [TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGTH, NINE, TEN]
FIGURAS = [JACK, QUEEN, KING]


class ObtieneBlackJack(Exception):
    pass

class ValorSobreBlackJack(Exception):
    pass

class MaximoJugadoresAlcanzado(Exception):
    pass

class MinimoJugadoresDisponible(Exception):
    pass

class JugadorNoEncontrado(Exception):
    pass

class JugadorPlantado(Exception):
    pass

class CartasAgotadas(Exception):
    pass


class CartaInglesa():
    def __init__(self, nombre, valores, pinta):
        self.nombre = nombre
        self.valores = valores
        self.pinta = pinta
        self.validar_valor()

    def __str__(self):
        return f"Carta de tipo {self.__class__} cuya pinta es {self.pinta} y cuyo valores posibles son {self.valores}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return self.nombre == other.nombre and self.pinta == other.pinta
    
    def validar_valor(self):
        """Valida que valor de carta corresponda con su tipo"""
        raise NotImplementedError("Método validar_valor no implementado")


class CartaNumerica(CartaInglesa):
    def validar_valor(self):
        if self.valores[0] < 2 or self.valores[0] > 10:
            raise ValueError(f"Valor {self.valores[0]} no corresponde al valor esperado de una carta numérica")


class CartaFigura(CartaInglesa):
    def __init__(self, nombre, pinta):
        super().__init__(nombre, [10], pinta)

    def validar_valor(self):
        if self.valores[0] != 10:
            raise ValueError(f"Valor {self.valores[0]} no corresponde al valor esperado de una figura")


class CartaAS(CartaInglesa):
    def __init__(self, nombre, pinta):
        super().__init__(nombre, [1, 11], pinta)

    def validar_valor(self):
        for valor in self.valores:
            if valor != 1 and valor != 11:
                raise ValueError(f"Valor {valor} no corresponde a los valores esperado de un AS")


class BarajaInglesa:

    TOTAL_CON_JOKERS = 52
    TOTAL_SIN_JOKERS = TOTAL_CON_JOKERS - 4

    def __init__(self):
        self.total = self.__class__.TOTAL_SIN_JOKERS
        self.cartas_restantes = self.total
        self.cartas_disponibles = []
        self._inicializar_baraja()

    def __str__(self):
        return f"total cartas: {self.total_cartas}, cartas restantes: {self.cartas_restantes}"

    def _inicializar_baraja(self):
        for pinta in PINTAS:
            self.cartas_disponibles.append(CartaAS(AS, pinta))
            self.cartas_disponibles.append(CartaNumerica(TWO, [2], pinta))
            self.cartas_disponibles.append(CartaNumerica(THREE, [3], pinta))
            self.cartas_disponibles.append(CartaNumerica(FOUR, [4], pinta))
            self.cartas_disponibles.append(CartaNumerica(FIVE, [5], pinta))
            self.cartas_disponibles.append(CartaNumerica(SIX, [6], pinta))
            self.cartas_disponibles.append(CartaNumerica(SEVEN, [7], pinta))
            self.cartas_disponibles.append(CartaNumerica(EIGTH, [8], pinta))
            self.cartas_disponibles.append(CartaNumerica(NINE, [9], pinta))
            self.cartas_disponibles.append(CartaNumerica(TEN, [10], pinta))
            self.cartas_disponibles.append(CartaFigura(JACK, pinta))
            self.cartas_disponibles.append(CartaFigura(QUEEN, pinta))
            self.cartas_disponibles.append(CartaFigura(KING, pinta))

    def obtener_carta(self):
        if self.cartas_restantes <= 0:
            raise CartasAgotadas

        carta = random.choice(self.cartas_disponibles)
        self.cartas_disponibles.remove(carta)
        self.cartas_restantes = self.cartas_restantes - 1
        return carta


class Jugador:
    def __init__(self, nombre, numero):
        self.nombre = nombre
        self.numero = numero
        self.mano = []
        self.ases = []
        self.posibles_puntajes = []
        self.ultima_carta = None
        self.puntaje_final = 0

    def __str__(self):
        return f"nombre jugador: {self.nombre}, puntaje final: {self.puntaje_final}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return self.nombre == other.nombre and self.numero == other.numero

    def tomar_carta(self, carta):
        if isinstance(carta, CartaAS):
            self.ases.append(carta)
        else:
            self.mano.append(carta)

        self.ultima_carta = carta
        self.sumar_puntos()

    def plantarse(self):
        self.puntaje_final = self.obtener_maximo_puntaje_actual()
        raise JugadorPlantado
    
    def sumar_puntos(self):
        puntaje_temp = 0

        for carta in self.mano:
            puntaje_temp = puntaje_temp + carta.valores[0]
            if puntaje_temp == BLACK_JACK:
                self.puntaje_final = puntaje_temp
                raise ObtieneBlackJack
            elif puntaje_temp > BLACK_JACK:
                self.puntaje_final = puntaje_temp
                raise ValorSobreBlackJack
        
        posible_perdedor = False
        puntajes_con_ases = []
        for carta in self.ases:
            extra_value = 0
            if len(self.ases) > 1:
                extra_value =  len(self.ases) - 1
            for valor in carta.valores:
                puntaje_temp_aux = puntaje_temp
                puntaje_temp_aux = puntaje_temp_aux + valor + extra_value
                if puntaje_temp == BLACK_JACK:
                    self.puntaje_final = puntaje_temp_aux
                    raise ObtieneBlackJack
                elif puntaje_temp > BLACK_JACK:
                    if not posible_perdedor:
                        posible_perdedor = True
                    else:
                        self.puntaje_final = puntaje_temp_aux
                        raise ValorSobreBlackJack
                else:
                    puntajes_con_ases.append(puntaje_temp_aux)
            break

        if puntajes_con_ases:
            self.posibles_puntajes = puntajes_con_ases
        else:
            self.posibles_puntajes = []
            self.posibles_puntajes.append(puntaje_temp)

    def obtener_mano(self):
        cartas = []
        for carta in self.mano:
            cartas.append(carta)
        
        for carta in self.ases:
            cartas.append(carta)

        return cartas
    
    def obtener_maximo_puntaje_actual(self):
        puntaje_max = 0 
        for puntaje in self.posibles_puntajes:
            if puntaje >= puntaje_max and puntaje <= BLACK_JACK:
                puntaje_max = puntaje
        
        return puntaje_max

    def reset(self):
        self.mano = []
        self.ases = []
        self.posibles_puntajes = []
        self.ultima_carta = None
        self.puntaje_final = 0


class Croupier(Jugador):
    OBJETIVO_PUNTAJE = 17
    
    def sumar_puntos(self):
        super().sumar_puntos()
        for puntaje in self.posibles_puntajes:
            if puntaje >= self.__class__.OBJETIVO_PUNTAJE:
                self.puntaje_final = puntaje
                raise JugadorPlantado

    def dar_cartas_iniciales(self, baraja, jugador):
        """Repartir una carta a un jugador específico"""
        carta1 = baraja.obtener_carta() 
        carta2 = baraja.obtener_carta()
        jugador.tomar_carta(carta1)
        jugador.tomar_carta(carta2)
    
    def dar_carta(self, baraja, jugador):
        carta = baraja.obtener_carta() 
        jugador.tomar_carta(carta)

        return carta

class RondaBlackJack:
    def __init__(self, croupier, jugadores = []):
        self.croupier = croupier
        self.jugadores = jugadores
        self.baraja = BarajaInglesa()
        self.jugadores_pendientes = [jugador.numero for jugador in self.jugadores]
        self.jugadores_en_competencia = [jugador.numero for jugador in self.jugadores]
        #self.jugadores = self.jugadores.copy()
        self.ganadores = []

    def dar_mano_inicial(self):
        jugadores_pendientes_aux = self.jugadores_pendientes.copy()
        for numero_jugador in self.jugadores_pendientes:
            try:
                jugador = obtener_jugador(numero_jugador, self.jugadores)
                self.croupier.dar_cartas_iniciales(self.baraja, jugador)
            except JugadorPlantado as jp:
                jugadores_pendientes_aux.remove(numero_jugador)
                continue
        
        self.jugadores_pendientes = jugadores_pendientes_aux
            

    def dar_carta(self, numero_jugador):
        if numero_jugador in self.jugadores_pendientes:
            jugador = obtener_jugador(numero_jugador, self.jugadores)
        else:
            raise JugadorPlantado

        try:
            self.croupier.dar_carta(self.baraja, jugador)
        except CartasAgotadas:
            raise
        except ValorSobreBlackJack:
            self.jugadores_en_competencia.remove(numero_jugador)
            self.jugadores_pendientes.remove(numero_jugador)
        except ObtieneBlackJack:
            self.jugadores_pendientes.remove(numero_jugador)
        except JugadorPlantado:
            self.jugadores_pendientes.remove(numero_jugador)


    def plantar_jugador(self, numero_jugador):
        if numero_jugador in self.jugadores_pendientes:
            jugador = obtener_jugador(numero_jugador, self.jugadores)
        else:
            raise JugadorPlantado

        self.jugadores_pendientes.remove(numero_jugador)
        jugador.plantarse()
    
    def determinar_ganador(self):
        puntaje_maximo = 0
        for numero_jugador in self.jugadores_en_competencia:
            jugador = obtener_jugador(numero_jugador, self.jugadores)
            if jugador.puntaje_final >= puntaje_maximo:
                puntaje_maximo = jugador.puntaje_final

        for numero_jugador in self.jugadores_en_competencia:
            jugador = obtener_jugador(numero_jugador, self.jugadores)
            if jugador.puntaje_final == puntaje_maximo:
                self.ganadores.append(jugador)


class MesaBlackJack:
    def __init__(self, id):
        self.id = id
        self.rondas_jugadas = 0
        self.ronda_actual = None
        self.croupier = Croupier("Croupier", 0)
        self.jugadores = [self.croupier]

    def __str__(self):
        return f"Mesa {self.id} \n rondas jugadas: {self.rondas_jugadas} \n jugadores mesa: {self.jugadores} \n estado: {'Jugando ronda' if self.ronda_actual == None else 'En espera de inicio de ronda'}"

    def nueva_ronda(self):
        self.ronda_actual = RondaBlackJack(self.croupier, self.jugadores)
        
    def terminar_ronda(self):
        self.rondas_jugadas = self.rondas_jugadas + 1
        self.ronda_actual.determinar_ganador()
        if not self.ronda_actual.ganadores:
            mensaje_final = "* !Partida Terminada! *\n* No quedan jugadores en competencia, se considera empate *"
        elif len(self.ronda_actual.ganadores) > 1:
            mensaje_final = "* !Partida Terminada! *\n* Hay mas de un ganador, se considera empate, Los ganadores son los siguientes: *\n"
            for ganador in self.ronda_actual.ganadores:
                mensaje_final = f"{mensaje_final}- {ganador.nombre} con puntaje de {ganador.puntaje_final}\n"
        else:
            mensaje_final = f"* !Partida Terminada! *\n* El ganador es {self.ronda_actual.ganadores[0].nombre} con un puntaje de {self.ronda_actual.ganadores[0].puntaje_final} *"
        self.ronda_actual = None
        self.croupier.reset()
        for jugador in self.jugadores:
            jugador.reset()

        return mensaje_final
    
    def agregar_jugador(self, nuevo_jugador):
        if len(self.jugadores) >= 8 and self.ronda_actual is None:
            raise MaximoJugadoresAlcanzado

        self.jugadores.append(nuevo_jugador)

    def remover_jugador(self, numero_jugador):
        if len(self.jugadores) <= 1:
            raise MinimoJugadoresDisponible

        for jugador in self.jugadores:
            if jugador.numero == numero_jugador:
                if self.ronda_actual and self.ronda_actual.jugadores_en_competencia:
                    self.ronda_actual.jugadores_en_competencia.remove(numero_jugador)
                if self.ronda_actual and self.ronda_actual.jugadores_pendientes:
                    self.ronda_actual.jugadores_pendientes.remove(numero_jugador)
                
                self.jugadores.remove(jugador)

    
def obtener_jugador(numero_jugador, jugadores=[]):
    for jugador in jugadores:
        if jugador.numero == numero_jugador:
            return jugador
    
    raise JugadorNoEncontrado

def obtener_carta_desde_string(string_carta = ""):
    cartas = []
    for carta in string_carta.split(TOKEN_SEPARACION_CARTAS, 1):
        tipo, pinta = carta.split(TOKEN_SEPARACION_DATOS_CARTA, 1)
        tipo = tipo.strip()
        pinta = pinta.strip()
        if tipo == AS:
            cartas.append(CartaAS(AS, pinta))
        elif tipo in FIGURAS:
            cartas.append(CartaFigura(tipo, pinta))
        elif tipo in NUMERICAS:
            valor = 2
            for num in NUMERICAS:
                if tipo == num:
                    break
                valor = valor + 1 
            cartas.append(CartaNumerica(tipo, [valor], pinta))
    
    if len(cartas) > 1:
        return cartas[0], cartas[1]
    
    return cartas[0]