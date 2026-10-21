DIMENSION = 10

BARCOS = {
    "Portaaviones": 4,
    "Crucero 1": 3,
    "Crucero 2": 3,
    "Destructor 1": 2,
    "Destructor 2": 2,
    "Destructor 3": 2,
    "Lancha 1": 1,
    "Lancha 2": 1,
    "Lancha 3": 1,
    "Lancha 4": 1,
}

AGUA = "~"
BARCO = "B"
TOCADO = "x"
FALLO = "o"

# Orientaciones: (cambio de fila, cambio de columna) por cada casilla del barco
ORIENTACIONES = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "O": (0, -1)}

# Dificultad adaptativa
TURNOS_IA_SIN_ACIERTO = 10       
ACIERTOS_JUGADOR_SEGUIDOS = 3    
TRAMPAS_POR_TURNO = 2            