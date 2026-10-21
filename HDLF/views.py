from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import servicios
from .models import Partida


def partida_de_sesion(request):
    partida_id = request.session.get("partida_id")
    if partida_id is None:
        return None
    return Partida.objects.filter(pk=partida_id).first()


def coordenada_valida(texto):
    return texto.isdigit() and 0 <= int(texto) <= 9


def inicio(request):
    partida = partida_de_sesion(request)
    jugando = partida is not None and partida.estado == Partida.Estado.EN_CURSO
    if partida is None:
        tablero = servicios.tablero_vacio()
    else:
        tablero = servicios.construir_tablero(partida)
    contexto = {
        "tablero": tablero,
        "columnas": range(10),
        "jugando": jugando,
        "disparos_restantes": servicios.disparos_restantes(partida) if jugando else 0,
    }
    return render(request, "HDLF/tablero.html", contexto)


@require_POST
def empezar(request):
    partida = servicios.crear_partida()
    request.session["partida_id"] = partida.pk
    messages.info(request, "Partida nueva, ¡suerte!")
    return redirect("inicio")


@require_POST
def disparar(request):
    partida = partida_de_sesion(request)
    if partida is None or partida.estado != Partida.Estado.EN_CURSO:
        return redirect("inicio")

    fila = request.POST.get("fila", "")
    columna = request.POST.get("columna", "")
    if not (coordenada_valida(fila) and coordenada_valida(columna)):
        messages.error(request, "Coordenadas incorrectas: solo números del 0 al 9")
        return redirect("inicio")

    i, j = int(fila), int(columna)
    resultado = servicios.registrar_disparo(partida, i, j)
    if resultado == "repetido":
        messages.warning(request, "Ya has disparado a esa casilla, prueba otra")
    elif resultado == "tocado":
        messages.success(request, f"¡Tocado en {i},{j}!")
    else:
        messages.info(request, f"Agua en {i},{j}")

    if partida.estado == Partida.Estado.GANADA:
        messages.success(request, "¡Has hundido todos los barcos!")
    elif partida.estado == Partida.Estado.PERDIDA:
        messages.error(request, "Te has quedado sin disparos")
    return redirect("inicio")