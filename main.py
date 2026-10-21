from juego.clases import Tablero
from juego.funciones import (
    SalirDelJuego,
    bienvenida,
    elegir_dificultad,
    turno_jugador,
    turno_maquina,
    debe_hacer_trampa,
)


def jugar():
    bienvenida()
    dificultad = elegir_dificultad()
    jugador = Tablero("jugador")
    maquina = Tablero("maquina")
    aciertos_jugador = []   
    aciertos_maquina = []   
    try:
        while True:
            aciertos_jugador.append(turno_jugador(jugador, maquina))
            if maquina.derrotado():
                print("\n¡Enhorabuena, has hundido toda la flota enemiga! Has ganado.")
                break

            trampa = dificultad == "adaptativa" and debe_hacer_trampa(aciertos_jugador, aciertos_maquina)
            aciertos_maquina.append(turno_maquina(jugador, trampa))
            if jugador.derrotado():
                print("\nLa máquina ha hundido toda tu flota. Has perdido.")
                break
    except SalirDelJuego:
        print("\nHas salido de la partida. ¡Hasta la próxima!")


if __name__ == "__main__":
    jugar()