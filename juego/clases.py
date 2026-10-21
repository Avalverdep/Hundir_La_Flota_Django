import random

from .variables import DIMENSION, BARCOS, AGUA, BARCO, TOCADO, FALLO, ORIENTACIONES


class Tablero:
    def __init__(self, id_jugador):
        self.id_jugador = id_jugador
        self.dimension = DIMENSION
        self.barcos = BARCOS
        # Lo que hay de verdad: barcos, impactos y fallos recibidos
        self.tablero_barcos = self.crear_tablero_vacio()
        # Lo que ve el rival: solo los disparos recibidos, sin barcos
        self.tablero_disparos = self.crear_tablero_vacio()
        self.posiciones = {}         
        self.barco_en_casilla = {}   
        self.colocar_barcos()

    def crear_tablero_vacio(self):
        tablero = []
        for i in range(self.dimension):
            tablero.append([AGUA] * self.dimension)
        return tablero

    
    def colocar_barcos(self):
        
        flota = sorted(self.barcos.items(), key=lambda barco: barco[1], reverse=True)
        for nombre, eslora in flota:
            colocado = False
            while not colocado:
                fila = random.randrange(self.dimension)
                columna = random.randrange(self.dimension)
                orientacion = random.choice(list(ORIENTACIONES))
                casillas = self.casillas_del_barco(fila, columna, eslora, orientacion)
                if casillas is not None and self.estan_libres(casillas):
                    for f, c in casillas:
                        self.tablero_barcos[f][c] = BARCO
                        self.barco_en_casilla[(f, c)] = nombre
                    self.posiciones[nombre] = casillas
                    colocado = True

    def casillas_del_barco(self, fila, columna, eslora, orientacion):
        """Casillas que ocuparía el barco, o None si se sale del tablero."""
        cambio_fila, cambio_columna = ORIENTACIONES[orientacion]
        casillas = []
        for i in range(eslora):
            f = fila + cambio_fila * i
            c = columna + cambio_columna * i
            if not (0 <= f < self.dimension and 0 <= c < self.dimension):
                return None
            casillas.append((f, c))
        return casillas

    def estan_libres(self, casillas):
        
        for f, c in casillas:
            for vecino_f in range(f - 1, f + 2):
                for vecino_c in range(c - 1, c + 2):
                    dentro = 0 <= vecino_f < self.dimension and 0 <= vecino_c < self.dimension
                    if dentro and self.tablero_barcos[vecino_f][vecino_c] != AGUA:
                        return False
        return True

    # ---------- disparos ----------
    def disparar(self, fila, columna):
        
        if self.tablero_disparos[fila][columna] != AGUA:
            return "repetido"
        if self.tablero_barcos[fila][columna] == BARCO:
            self.tablero_barcos[fila][columna] = TOCADO
            self.tablero_disparos[fila][columna] = TOCADO
            if self.esta_hundido(self.barco_en_casilla[(fila, columna)]):
                return "hundido"
            return "tocado"
        self.tablero_barcos[fila][columna] = FALLO
        self.tablero_disparos[fila][columna] = FALLO
        return "agua"

    def esta_hundido(self, nombre):
        for f, c in self.posiciones[nombre]:
            if self.tablero_barcos[f][c] != TOCADO:
                return False
        return True

    def nombre_barco(self, fila, columna):
        return self.barco_en_casilla[(fila, columna)]

    # ---------- estado (siempre calculado, nunca guardado) ----------
    def barcos_restantes(self):
        total = 0
        for nombre in self.posiciones:
            if not self.esta_hundido(nombre):
                total += 1
        return total

    def derrotado(self):
        return self.barcos_restantes() == 0

    def casillas_sin_disparar(self):
        casillas = []
        for f in range(self.dimension):
            for c in range(self.dimension):
                if self.tablero_disparos[f][c] == AGUA:
                    casillas.append((f, c))
        return casillas

    def casillas_con_barco(self):
        """Casillas con barco que todavía no han sido tocadas."""
        casillas = []
        for f in range(self.dimension):
            for c in range(self.dimension):
                if self.tablero_barcos[f][c] == BARCO:
                    casillas.append((f, c))
        return casillas