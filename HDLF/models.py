from django.db import models

# Create your models here.
from django.db import models


class Partida(models.Model):
    class Estado(models.TextChoices):
        EN_CURSO = "en_curso", "En curso"
        GANADA = "ganada", "Ganada"
        PERDIDA = "perdida", "Perdida"

    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.EN_CURSO)
    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Partida {self.pk} ({self.estado})"


class Jugador(models.TextChoices):
    HUMANO = "humano", "Humano"
    MAQUINA = "maquina", "Máquina"


class PosicionBarco(models.Model):
   
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="posiciones")
    propietario = models.CharField(max_length=10, choices=Jugador.choices)
    barco = models.PositiveSmallIntegerField()   # identifica a qué barco pertenece la casilla
    fila = models.PositiveSmallIntegerField()
    columna = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["partida", "propietario", "fila", "columna"],
                name="casilla_barco_unica",
            ),
            models.CheckConstraint(
                condition=models.Q(fila__lte=9, columna__lte=9),
                name="posicion_dentro_tablero",
            ),
        ]


class Disparo(models.Model):
    """Quién dispara y a dónde. Si fue tocado o agua se calcula, no se guarda."""
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name="disparos")
    tirador = models.CharField(max_length=10, choices=Jugador.choices)
    fila = models.PositiveSmallIntegerField()
    columna = models.PositiveSmallIntegerField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["partida", "tirador", "fila", "columna"],
                name="disparo_unico",
            ),
            models.CheckConstraint(
                condition=models.Q(fila__lte=9, columna__lte=9),
                name="disparo_dentro_tablero",
            ),
        ]