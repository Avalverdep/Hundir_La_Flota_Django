from django.contrib import admin
from .models import Partida, PosicionBarco, Disparo

admin.site.register([Partida, PosicionBarco, Disparo])