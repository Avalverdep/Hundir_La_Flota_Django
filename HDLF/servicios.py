from juego.clases import Tablero
from juego.funciones import (
    debe_hacer_trampa,
    elegir_casilla_aleatoria,
    elegir_casilla_con_barco,
)
from juego.variables import BARCOS, TRAMPAS_POR_TURNO

from .models import Partida, PosicionBarco, Disparo, Jugador
from juego.variables import BARCOS, TOCADO, TRAMPAS_POR_TURNO

NOMBRES_BARCOS = list(BARCOS)  # PosicionBarco.barco guarda el índice en esta lista


# ---------- crear ----------
def crear_partida(dificultad=Partida.Dificultad.NORMAL):
    """Crea la partida y guarda los barcos de los dos jugadores."""
    if dificultad not in Partida.Dificultad.values:
        dificultad = Partida.Dificultad.NORMAL
    partida = Partida.objects.create(dificultad=dificultad)
    for propietario in (Jugador.HUMANO, Jugador.MAQUINA):
        tablero = Tablero(propietario)  # colocación aleatoria, distinta cada vez
        for nombre, casillas in tablero.posiciones.items():
            for fila, columna in casillas:
                PosicionBarco.objects.create(
                    partida=partida,
                    propietario=propietario,
                    barco=NOMBRES_BARCOS.index(nombre),
                    fila=fila,
                    columna=columna,
                )
    return partida


# ---------- reconstruir el estado desde la base de datos ----------
def cargar_estado(partida):
    """Devuelve (jugador, maquina, aciertos_jugador, aciertos_maquina).

    Los tableros se reconstruyen con los barcos guardados y repitiendo los
    disparos en orden. Los aciertos por turno salen de agrupar los disparos
    seguidos del mismo tirador (un turno solo acaba al fallar)."""
    posiciones = {Jugador.HUMANO: {}, Jugador.MAQUINA: {}}
    for pos in partida.posiciones.all():
        nombre = NOMBRES_BARCOS[pos.barco]
        posiciones[pos.propietario].setdefault(nombre, []).append((pos.fila, pos.columna))
    jugador = Tablero(Jugador.HUMANO, posiciones[Jugador.HUMANO])
    maquina = Tablero(Jugador.MAQUINA, posiciones[Jugador.MAQUINA])

    turnos = []  # [[tirador, aciertos], ...]
    for d in partida.disparos.order_by("id"):
        objetivo = maquina if d.tirador == Jugador.HUMANO else jugador
        resultado = objetivo.disparar(d.fila, d.columna)
        if not turnos or turnos[-1][0] != d.tirador:
            turnos.append([d.tirador, 0])
        if resultado != "agua":
            turnos[-1][1] += 1
    aciertos_jugador = [a for t, a in turnos if t == Jugador.HUMANO]
    aciertos_maquina = [a for t, a in turnos if t == Jugador.MAQUINA]
    return jugador, maquina, aciertos_jugador, aciertos_maquina


# ---------- jugar ----------
def registrar_disparo(partida, fila, columna):
    """Dispara el jugador y, si falla, juega la máquina. Devuelve un resumen."""
    jugador, maquina, _, _ = cargar_estado(partida)
    resultado = maquina.disparar(fila, columna)
    resumen = {"resultado": resultado, "barco": None, "maquina": [], "trampa": False}
    if resultado == "repetido":
        return resumen
    if resultado == "hundido":
        resumen["barco"] = maquina.nombre_barco(fila, columna)
    Disparo.objects.create(partida=partida, tirador=Jugador.HUMANO, fila=fila, columna=columna)

    if maquina.derrotado():
        partida.estado = Partida.Estado.GANADA
        partida.save()
    elif resultado == "agua":
        turno_maquina(partida, resumen)
    return resumen  

def rendirse(partida):
    """Abandonar la partida en curso cuenta como perderla."""
    if partida.estado == Partida.Estado.EN_CURSO:
        partida.estado = Partida.Estado.PERDIDA
        partida.save()


def turno_maquina(partida, resumen):
    jugador, _, aciertos_jugador, aciertos_maquina = cargar_estado(partida)
    trampa = (
        partida.dificultad == Partida.Dificultad.ADAPTATIVA
        and debe_hacer_trampa(aciertos_jugador, aciertos_maquina)
    )
    resumen["trampa"] = trampa
    trampas_restantes = TRAMPAS_POR_TURNO if trampa else 0
    while True:
        if trampas_restantes > 0:
            fila, columna = elegir_casilla_con_barco(jugador)
            trampas_restantes -= 1
        else:
            fila, columna = elegir_casilla_aleatoria(jugador)
        resultado = jugador.disparar(fila, columna)
        barco = jugador.nombre_barco(fila, columna) if resultado == "hundido" else None
        Disparo.objects.create(partida=partida, tirador=Jugador.MAQUINA, fila=fila, columna=columna)
        resumen["maquina"].append({"fila": fila, "columna": columna, "resultado": resultado, "barco": barco})
        if jugador.derrotado():
            partida.estado = Partida.Estado.PERDIDA
            partida.save()
            return
        if resultado == "agua":
            return


# ---------- lo que se pinta ----------
def tablero_vacio():
    return Tablero("vacio", {}).tablero_disparos  # sin barcos: solo agua


def datos_para_pintar(partida):
    """(tablero de disparos a la máquina, tablero propio, barcos de cada uno)."""
    if partida is None:
        vacio = tablero_vacio()
        return vacio, vacio, 0, 0
    jugador, maquina, _, _ = cargar_estado(partida)
    return (
        maquina.tablero_disparos,
        jugador.tablero_barcos,
        maquina.barcos_restantes(),
        jugador.barcos_restantes(),
    )
def resumen_flota(tablero, ver_impactos):
    """Lista de barcos del tablero, del más grande al más pequeño.
    ver_impactos: True para tu flota; en la del enemigo solo se sabe si está hundido."""
    barcos = []
    for nombre in NOMBRES_BARCOS:
        casillas = tablero.posiciones.get(nombre, [])
        tocadas = sum(1 for f, c in casillas if tablero.tablero_barcos[f][c] == TOCADO)
        barcos.append({
            "nombre": nombre,
            "eslora": BARCOS[nombre],
            "hundido": bool(casillas) and tablero.esta_hundido(nombre),
            "tocadas": tocadas if ver_impactos else None,
        })
    return barcos


def flotas(partida):
    """(tu flota, flota enemiga) para el cuadro de barcos. Sin partida, la flota intacta."""
    if partida is None:
        vacia = Tablero("vacio", {})
        return resumen_flota(vacia, True), resumen_flota(vacia, False)
    jugador, maquina, _, _ = cargar_estado(partida)
    return resumen_flota(jugador, True), resumen_flota(maquina, False)