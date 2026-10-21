import random

from .variables import (
    DIMENSION,
    TURNOS_IA_SIN_ACIERTO,
    ACIERTOS_JUGADOR_SEGUIDOS,
    TRAMPAS_POR_TURNO,
)


class SalirDelJuego(Exception):
    pass


# ---------- presentación ----------
def bienvenida():
    print("=" * 46)
    print("          HUNDIR LA FLOTA")
    print("=" * 46)
    print("Tú y la máquina tenéis 10 barcos en un tablero de 10x10.")
    print("Empiezas tú. Si aciertas, repites turno; si fallas, dispara la máquina.")
    print("Gana quien hunda primero toda la flota del rival.")
    print("Escribe las coordenadas como fila,columna (por ejemplo 3,4).")
    print("También puedes escribir 'ver' (muestra los barcos de la máquina) o 'salir'.")
    print("Leyenda: B barco | x tocado | o agua disparada | ~ agua")
    print()


def elegir_dificultad():
    print("Dificultad:")
    print("  1. Normal (la máquina dispara al azar)")
    print("  2. Adaptativa (la máquina puede hacer trampas si le va mal o si vas muy bien)")
    while True:
        opcion = input("Elige 1 o 2: ").strip()
        if opcion == "1":
            return "normal"
        if opcion == "2":
            return "adaptativa"
        print("Opción no válida")


def formatear_tablero(matriz):
    lineas = ["   " + " ".join(str(c) for c in range(DIMENSION))]
    for num_fila, fila in enumerate(matriz):
        lineas.append(f"{num_fila}  " + " ".join(fila))
    return lineas


def imprimir_tableros(jugador, maquina, ver_barcos_maquina=False):
    izquierda = formatear_tablero(jugador.tablero_barcos)
    if ver_barcos_maquina:
        derecha = formatear_tablero(maquina.tablero_barcos)
    else:
        derecha = formatear_tablero(maquina.tablero_disparos)
    print()
    print("TU TABLERO".center(22) + "     " + "TABLERO DE LA MÁQUINA".center(22))
    for izq, der in zip(izquierda, derecha):
        print(izq + "     " + der)
    print(f"Barcos restantes -> tú: {jugador.barcos_restantes()} | máquina: {maquina.barcos_restantes()}")


def mostrar_resultado(resultado, tablero, fila, columna):
    if resultado == "agua":
        print("Agua")
    elif resultado == "tocado":
        print("¡Tocado!")
    elif resultado == "hundido":
        print(f"¡Hundido! ({tablero.nombre_barco(fila, columna)})")


# ---------- entrada del usuario ----------
def pedir_accion():
    while True:
        texto = input("Tu disparo (fila,columna), 'ver' o 'salir': ").strip().lower()
        if texto == "salir":
            return ("salir",)
        if texto == "ver":
            return ("ver",)
        partes = texto.replace(",", " ").split()
        if len(partes) != 2:
            print("Formato incorrecto. Ejemplo: 3,4")
            continue
        try:
            fila, columna = int(partes[0]), int(partes[1])
        except ValueError:
            print("Sólo se pueden introducir números. Ejemplo: 3,4")
            continue
        if not (0 <= fila < DIMENSION and 0 <= columna < DIMENSION):
            print(f"Las coordenadas deben estar entre 0 y {DIMENSION - 1}")
            continue
        return ("disparo", fila, columna)


# ---------- turnos ----------
def turno_jugador(jugador, maquina):
    """Devuelve cuántos aciertos has hecho en este turno."""
    aciertos = 0
    while True:
        imprimir_tableros(jugador, maquina)
        accion = pedir_accion()
        if accion[0] == "salir":
            raise SalirDelJuego
        if accion[0] == "ver":
            imprimir_tableros(jugador, maquina, ver_barcos_maquina=True)
            continue
        _, fila, columna = accion
        resultado = maquina.disparar(fila, columna)
        if resultado == "repetido":
            print("Ya has disparado a esa casilla, prueba otra")
            continue
        mostrar_resultado(resultado, maquina, fila, columna)
        if resultado == "agua":
            return aciertos
        aciertos += 1
        if maquina.derrotado():
            return aciertos


def elegir_casilla_aleatoria(tablero):
    return random.choice(tablero.casillas_sin_disparar())


def elegir_casilla_con_barco(tablero):
    return random.choice(tablero.casillas_con_barco())


def turno_maquina(jugador, trampa=False):
    """Devuelve cuántos aciertos ha hecho la máquina en este turno."""
    print("\n--- Turno de la máquina ---")
    aciertos = 0
    trampas_restantes = TRAMPAS_POR_TURNO if trampa else 0
    if trampa:
        print("¡La máquina afina la puntería!")
    while True:
        if trampas_restantes > 0:
            fila, columna = elegir_casilla_con_barco(jugador)
            trampas_restantes -= 1
        else:
            fila, columna = elegir_casilla_aleatoria(jugador)
        resultado = jugador.disparar(fila, columna)
        print(f"La máquina dispara a ({fila}, {columna}): ", end="")
        mostrar_resultado(resultado, jugador, fila, columna)
        if resultado == "agua":
            return aciertos
        aciertos += 1
        if jugador.derrotado():
            return aciertos


# ---------- dificultad adaptativa ----------
def turnos_seguidos_sin_acierto(aciertos_por_turno):
    total = 0
    for aciertos in reversed(aciertos_por_turno):
        if aciertos > 0:
            break
        total += 1
    return total


def debe_hacer_trampa(aciertos_jugador, aciertos_maquina):
    if turnos_seguidos_sin_acierto(aciertos_maquina) >= TURNOS_IA_SIN_ACIERTO:
        return True
    if aciertos_jugador and aciertos_jugador[-1] >= ACIERTOS_JUGADOR_SEGUIDOS:
        return True
    return False





def crear_tablero():
    tablero = []
    barco_h = 0, 1, 2, 3
    barco_v = 3, 4, 5
    for i in range(0, 10):
        fila = [" "] * 10
        tablero.append(fila)
    for x in barco_h:
        tablero[1][x] = "B"
    for y in barco_v:
        tablero[y][3] = "B"
    return tablero


def barcos_restantes(tablero):
    total = 0
    for fila in tablero:
        total += fila.count("B")
    return total


def disparar(tablero, i, j):
    if tablero[i][j] == "x" or tablero[i][j] == "o":
        return "repetido"
    if tablero[i][j] == "B":
        tablero[i][j] = "x"
        return "tocado"
    tablero[i][j] = "o"
    return "agua"