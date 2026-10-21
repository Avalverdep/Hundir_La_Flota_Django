from juego.funciones import crear_tablero, barcos_restantes, disparar
from .models import Partida, PosicionBarco, Disparo, Jugador

MAX_DISPAROS = 10


def tablero_vacio():
    tablero = []
    for i in range(10):
        tablero.append([" "] * 10)
    return tablero


def crear_partida():
    """Crea la partida y guarda cada casilla de barco en la base de datos."""
    partida = Partida.objects.create()
    plano = crear_tablero()  
    for i, fila in enumerate(plano):
        for j, casilla in enumerate(fila):
            if casilla == "B":
                PosicionBarco.objects.create(
                    partida=partida, propietario=Jugador.MAQUINA, barco=1, fila=i, columna=j
                )
    return partida


def construir_tablero(partida, ver_barcos=False):
    """Reconstruye la lista 2D (la del mini) a partir de la base de datos."""
    tablero = tablero_vacio()
    for pos in partida.posiciones.filter(propietario=Jugador.MAQUINA):
        tablero[pos.fila][pos.columna] = "B"
    for d in partida.disparos.filter(tirador=Jugador.HUMANO):
        if tablero[d.fila][d.columna] == "B":
            tablero[d.fila][d.columna] = "x"
        else:
            tablero[d.fila][d.columna] = "o"
    if not ver_barcos:
        for fila in tablero:
            for j, casilla in enumerate(fila):
                if casilla == "B":
                    fila[j] = " "
    return tablero


def disparos_restantes(partida):
    return MAX_DISPAROS - partida.disparos.count()


def registrar_disparo(partida, i, j):
    tablero = construir_tablero(partida, ver_barcos=True)
    resultado = disparar(tablero, i, j)
    if resultado != "repetido":
        Disparo.objects.create(partida=partida, tirador=Jugador.HUMANO, fila=i, columna=j)
        if barcos_restantes(tablero) == 0:
            partida.estado = Partida.Estado.GANADA
        elif disparos_restantes(partida) <= 0:
            partida.estado = Partida.Estado.PERDIDA
        partida.save()
    return resultado